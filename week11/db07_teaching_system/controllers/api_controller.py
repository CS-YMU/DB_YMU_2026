import json
from urllib.parse import parse_qs, urlparse

from models.database import DatabaseUnavailable, check_database
from models.exercise_model import ExerciseModel
from models.normalization_engine import (
    check_normal_form,
    compute_closure,
    compute_minimal_cover,
    find_candidate_keys,
    test_lossless_join,
)
from models.teaching_cases import CASES


class ApiController:
    @staticmethod
    def handle(handler):
        parsed = urlparse(handler.path)
        path = parsed.path

        # GET 路由
        if handler.command == "GET":
            if path == "/api/db-status":
                return ApiController.db_status(handler)
            if path == "/api/topics":
                return ApiController.topics(handler)
            if path == "/api/exercises":
                params = parse_qs(parsed.query)
                topic_key = params.get("topic_key", [None])[0]
                return ApiController.exercises(handler, topic_key)
            if path == "/api/cases":
                return ApiController.cases(handler)
            return ApiController.send_json(handler, {"ok": False, "message": "API 不存在。"}, 404)

        # POST 路由
        if handler.command == "POST":
            if path == "/api/submit":
                return ApiController.submit(handler)
            if path == "/api/compute-closure":
                return ApiController.handle_compute_closure(handler)
            if path == "/api/find-keys":
                return ApiController.handle_find_keys(handler)
            if path == "/api/minimal-cover":
                return ApiController.handle_minimal_cover(handler)
            if path == "/api/normal-form":
                return ApiController.handle_normal_form(handler)
            if path == "/api/chase-test":
                return ApiController.handle_chase_test(handler)
            return ApiController.send_json(handler, {"ok": False, "message": "API 不存在。"}, 404)

    # ==================== 原有 API ====================

    @staticmethod
    def db_status(handler):
        try:
            db_name = check_database()
            payload = {"ok": True, "source": "database", "database": db_name}
        except DatabaseUnavailable as exc:
            payload = {"ok": False, "source": "fallback", "message": str(exc)}
        return ApiController.send_json(handler, payload)

    @staticmethod
    def topics(handler):
        return ApiController.send_json(handler, {"ok": True, **ExerciseModel.list_topics()})

    @staticmethod
    def exercises(handler, topic_key):
        return ApiController.send_json(handler, {"ok": True, **ExerciseModel.list_exercises(topic_key)})

    @staticmethod
    def submit(handler):
        body = ApiController._read_body(handler)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return ApiController.send_json(handler, {"ok": False, "message": "JSON 格式错误。"}, 400)

        result = ExerciseModel.submit_answer(
            payload.get("exercise_id"),
            payload.get("student_name", ""),
            payload.get("submitted_answer", ""),
        )
        return ApiController.send_json(handler, result)

    # ==================== 教学案例 API ====================

    @staticmethod
    def cases(handler):
        return ApiController.send_json(handler, {"ok": True, "data": CASES})

    # ==================== 规范化算法 API ====================

    @staticmethod
    def handle_compute_closure(handler):
        body = ApiController._read_body(handler)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return ApiController.send_json(handler, {"ok": False, "message": "JSON 格式错误。"}, 400)

        x = payload.get("x", "")
        fds = payload.get("fds", [])
        attrs = payload.get("attributes", None)

        if not x:
            return ApiController.send_json(handler, {"ok": False, "message": "请输入属性集 X。"}, 400)
        if not fds:
            return ApiController.send_json(handler, {"ok": False, "message": "请输入函数依赖集。"}, 400)

        try:
            result = compute_closure(x, fds, attrs)
            return ApiController.send_json(handler, {"ok": True, **result})
        except Exception as exc:
            return ApiController.send_json(handler, {"ok": False, "message": f"计算错误：{exc}"}, 500)

    @staticmethod
    def handle_find_keys(handler):
        body = ApiController._read_body(handler)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return ApiController.send_json(handler, {"ok": False, "message": "JSON 格式错误。"}, 400)

        attrs = payload.get("attributes", [])
        fds = payload.get("fds", [])

        if not attrs:
            return ApiController.send_json(handler, {"ok": False, "message": "请输入属性集。"}, 400)
        if not fds:
            return ApiController.send_json(handler, {"ok": False, "message": "请输入函数依赖集。"}, 400)

        try:
            result = find_candidate_keys(attrs, fds)
            return ApiController.send_json(handler, {"ok": True, **result})
        except Exception as exc:
            return ApiController.send_json(handler, {"ok": False, "message": f"计算错误：{exc}"}, 500)

    @staticmethod
    def handle_minimal_cover(handler):
        body = ApiController._read_body(handler)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return ApiController.send_json(handler, {"ok": False, "message": "JSON 格式错误。"}, 400)

        fds = payload.get("fds", [])

        if not fds:
            return ApiController.send_json(handler, {"ok": False, "message": "请输入函数依赖集。"}, 400)

        try:
            result = compute_minimal_cover(fds)
            return ApiController.send_json(handler, {"ok": True, **result})
        except Exception as exc:
            return ApiController.send_json(handler, {"ok": False, "message": f"计算错误：{exc}"}, 500)

    @staticmethod
    def handle_normal_form(handler):
        body = ApiController._read_body(handler)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return ApiController.send_json(handler, {"ok": False, "message": "JSON 格式错误。"}, 400)

        attrs = payload.get("attributes", [])
        fds = payload.get("fds", [])

        if not attrs:
            return ApiController.send_json(handler, {"ok": False, "message": "请输入属性集。"}, 400)

        try:
            result = check_normal_form(attrs, fds)
            return ApiController.send_json(handler, {"ok": True, **result})
        except Exception as exc:
            return ApiController.send_json(handler, {"ok": False, "message": f"计算错误：{exc}"}, 500)

    @staticmethod
    def handle_chase_test(handler):
        body = ApiController._read_body(handler)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return ApiController.send_json(handler, {"ok": False, "message": "JSON 格式错误。"}, 400)

        attrs = payload.get("attributes", [])
        fds = payload.get("fds", [])
        decomposition = payload.get("decomposition", [])

        if not attrs or not fds or not decomposition:
            return ApiController.send_json(handler, {"ok": False, "message": "请输入属性集、函数依赖集和分解方案。"}, 400)

        try:
            result = test_lossless_join(attrs, fds, decomposition)
            return ApiController.send_json(handler, {"ok": True, **result})
        except Exception as exc:
            return ApiController.send_json(handler, {"ok": False, "message": f"计算错误：{exc}"}, 500)

    # ==================== 辅助方法 ====================

    @staticmethod
    def _read_body(handler):
        length = int(handler.headers.get("Content-Length", "0"))
        return handler.rfile.read(length).decode("utf-8") if length else "{}"

    @staticmethod
    def send_json(handler, payload, status=200):
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        handler.send_response(status)
        handler.send_header("Content-Type", "application/json; charset=utf-8")
        handler.send_header("Content-Length", str(len(data)))
        handler.end_headers()
        handler.wfile.write(data)
