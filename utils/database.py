import motor.motor_asyncio
import config
import datetime
import re

client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URI).dicopedia


class USER_DATABASE:
    async def user_find(user_id: int):
        """
        user_id (int) - 필수, 디스코드 유저 ID 입력
        """
        return await client.user.find_one({"_id": user_id})

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
        return {"status": "success", "content": "사용자 설명이 업데이트되었어요."}


class WIKI_DATABASE:
    async def wiki_find(wiki_name: str):
        """
        wiki_name (str) - 필수, 위키 이름 입력

        * todo : 정규식을 사용하여 알맞은 문서 정보가 없을 때 추천 문서를 보여주는 기능 추가
        """
        return await client.wiki.find_one({"_id": wiki_name})
