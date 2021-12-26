import datetime
import re

import config
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URI).dicopedia


class USER_DATABASE:    
    async def user_find(user_id: int):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        """
        return await client.user.find_one({"_id": user_id})
        # return await client.user.find_one({"userid": user_id})

    async def user_add(user_id: int):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        """
        return await client.user.insert_one(
            {
                "_id": user_id,
                "description": "아직 설명이 없습니다.",
                "created_at": datetime.datetime.now(),
            }
        )

    async def user_list(filter: dict = None):
        """
        filter (dict) - 선택, DICT 형식으로 입력
        """
        user_list = []
        if filter:
            async for i in client.user.find(filter):
                user_list.append(i)
        else:
            async for i in client.user.find({}):
                user_list.append(i)
        return user_list

    async def user_edit_description(user_id: int, new_description: str):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        new_description (str) - 필수, 30자를 넘지 않는 새로운 사용자 설명 입력
        """
        if len(new_description) > 30:
            return {"status": "failed", "content": "설명은 30자를 넘을 수 없어요."}
        await client.user.update_one(
            {"_id": user_id}, {"$set": {"description": new_description}}
        )
        # await client.user.update_one({"userid": user_id}, {"$set": {"description": new_description}})
        return {"status": "success", "content": "사용자 설명이 업데이트되었어요."}

    async def user_find_document(user_id: int):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        """
        coll = await client.wiki.find({"m": True})


class WIKI_DATABASE:
    async def wiki_find(wiki_name: str, user_id: int):
        """
        wiki_name (str) - 필수, 위키 문서 이름 입력
        user_id (int) - 필수, 요청한 유저 ID 입력

        * todo : 정규식을 사용하여 알맞은 문서 정보가 없을 때 추천 문서를 보여주는 기능 추가
        # """
        result = await client.wiki.find_one({"_id": wiki_name})
        if result is None:
            return None
        if result["acl"]["read_admin"] == True:
            if not user_id in config.OWNER_IDS:
                return {"status": "failed", "content": "일반 유저는 열람할 수 없는 문서에요."}
        return {"status": "success", "content": result}

    async def wiki_content_find(wiki_name: str, user_id: int, r: int = None):
        """
        wiki_name (str) - 필수, 위키 문서 이름 입력
        user_id: (int) - 필수, 요청한 유저 ID 입력
        r (int) - 선택, 확인하고 싶은 편집판(r) 번호 입력
        """
        result = await client.wiki.find_one({"_id": wiki_name})
        if result is None:
            return {"status": "failed", "content": "문서가 존재하지 않아요."}
        if result["acl"]["read_admin"] == True:
            if not user_id in config.OWNER_IDS:
                return {"status": "failed", "content": "일반 유저는 열람할 수 없는 문서에요."}
        if r:
            try:
                content = result["history"][f"r{r}"]
            except KeyError:
                return {"status": "failed", "content": f"해당하는 편집판(``r{r}판``)이 없어요."}
        else:
            rtip = []
            for i in result["history"]:
                if "r" in i:
                    rtip.append((int(i.replace("r", ""))))
            content = result["history"][f"r{len(rtip)}"]
            r = len(rtip)
        return {
            "status": "success",
            "content": content,
            "title": result["_id"],
            "r": str(r),
        }

    async def wiki_create(wiki_name: str, wiki_content: str, user_id: int):
        """
        wiki_name (str) - 필수, 위키 문서 이름 입력
        wiki_content (str) - 필수, 위키 문서 내용 입력
        user_id (int) - 필수, 위키 문서 변경자 입력
        """
        if (await WIKI_DATABASE.wiki_find(wiki_name, user_id)) != None:
            return {"status": "failed", "content": "이미 존재하는 문서에요."}
        await client.wiki.insert_one(
            {
                "_id": wiki_name,
                "created_at": datetime.datetime.now(),
                "acl": {"edit_admin": False, "read_admin": False},
                "reportNum": 0,
                "history": {
                    "r1": {
                        "content": wiki_content,
                        "author": user_id,
                        "updated_at": datetime.datetime.now(),
                    }
                },
            }
        )
        return {"status": "success", "content": "새로운 문서를 생성하였어요."}

    async def wiki_edit(wiki_name: str, wiki_content: str, user_id: int):
        """
        wiki_name (str) - 필수, 위키 문서 이름 입력
        wiki_content (str) - 필수, 위키 문서 내용 입력
        user_id (int) - 필수, 위키 문서 변경자 입력
        """
        find_result = await WIKI_DATABASE.wiki_find(wiki_name, user_id)
        rtip = []
        for i in find_result["content"]["history"]:
            if "r" in i:
                rtip.append((int(i.replace("r", ""))))
        if (
            find_result["content"]["acl"]["edit_admin"] == True
            or find_result["content"]["acl"]["read_admin"] == True
        ):
            if not user_id in config.OWNER_IDS:
                return {"status": "failed", "content": "일반 유저는 수정할 수 없는 문서에요."}
        edit_R = f"r{len(rtip)+1}"
        find_result["content"]["history"][edit_R] = {
            "content": wiki_content,
            "author": user_id,
            "updated_at": datetime.datetime.now(),
        }
        await client.wiki.update_one(
            {"_id": wiki_name}, {"$set": find_result["content"]}
        )
        return {"status": "success", "content": "문서를 수정하였어요."}

    async def wiki_search(keyword: str, user_id: int):
        """
        keyword (str) - 필수, 검색할 키워드 입력
        user_id (int) - 필수, 요청한 유저 ID 입력
        """
        result = client.wiki.find({'_id': {'$regex': keyword}})
        search_result = [i async for i in result]
        return search_result


    async def wiki_list(filter: dict = None):
        """
        filter (dict) - 선택, DICT 형식으로 입력
        """
        wiki_list = []
        if filter:
            async for i in client.wiki.find(filter):
                wiki_list.append(i)
        else:
            async for i in client.wiki.find({}):
                wiki_list.append(i)
        return wiki_list

    async def wiki_add_report(wiki_name: str, reportType: str, user_id: int):
        """
        wiki_name (str) - 필수, 신고된 문서 이름 입력
        reportType (str) - 필수, 신고 유형 입력
        user_id (int) - 필수, 신고한 유저 아이디 입력
        """
        try:
            c1 = await client.wiki.update_one(
                {"_id": wiki_name}, {"$inc": {"reportNum": 1}}
            )
            print(c1)
            c2 = await client.report.insert_one(
                {"wiki_name": wiki_name, "reportType": reportType, "reported_at": datetime.datetime.now(), "reportUser": user_id}
            )
            print(c2)
            if int((await client.wiki.find_one({"_id": wiki_name}))["reportNum"]) >= 5:
                c3 = await client.wiki.update_one(
                    {"_id": wiki_name}, {"$set": {"acl": {"edit_admin": True, "read_admin": True}}}
                )
                print(c3)
                return {"status": "success", "content": "신고가 5회 이상 접수되어 열람 불가 상태로 변경하였어요.."}
            return {"status": "success", "content": "신고가 접수되었어요."}
        except:
            return {"status": "fail", "content": f"\n{__import__('traceback').format_exc()}"}