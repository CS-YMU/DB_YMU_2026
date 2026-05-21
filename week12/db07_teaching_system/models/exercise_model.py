import json

from models.database import DatabaseUnavailable, get_connection
from models.seed_data import EXERCISES, TOPICS


class ExerciseModel:
    @staticmethod
    def list_topics():
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT topic_key, title, source_section, sort_order
                        FROM db07_topics
                        ORDER BY sort_order
                        """
                    )
                    return {"source": "database", "data": cursor.fetchall()}
        except DatabaseUnavailable as exc:
            topics = [
                {**topic, "source_section": "本地备用数据"}
                for topic in TOPICS
            ]
            return {"source": "fallback", "message": str(exc), "data": topics}

    @staticmethod
    def list_exercises(topic_key=None):
        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    if topic_key:
                        cursor.execute(
                            """
                            SELECT id, topic_key, question_type, question, options_json,
                                   answer, explanation, difficulty, sort_order
                            FROM db07_exercises
                            WHERE topic_key=%s
                            ORDER BY sort_order, id
                            """,
                            (topic_key,),
                        )
                    else:
                        cursor.execute(
                            """
                            SELECT id, topic_key, question_type, question, options_json,
                                   answer, explanation, difficulty, sort_order
                            FROM db07_exercises
                            ORDER BY topic_key, sort_order, id
                            """
                        )
                    return {"source": "database", "data": [_normalize(row) for row in cursor.fetchall()]}
        except DatabaseUnavailable as exc:
            rows = EXERCISES
            if topic_key:
                rows = [row for row in rows if row["topic_key"] == topic_key]
            return {"source": "fallback", "message": str(exc), "data": rows}

    @staticmethod
    def submit_answer(exercise_id, student_name, submitted_answer):
        exercise = ExerciseModel.find_exercise(exercise_id)
        if not exercise:
            return {"ok": False, "message": "练习题不存在。"}

        is_correct = str(submitted_answer).strip() == str(exercise["answer"]).strip()
        result = {
            "ok": True,
            "is_correct": is_correct,
            "correct_answer": exercise["answer"],
            "explanation": exercise["explanation"],
        }

        try:
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO db07_student_attempts
                            (exercise_id, student_name, submitted_answer, is_correct)
                        VALUES (%s, %s, %s, %s)
                        """,
                        (exercise_id, student_name or "匿名学生", submitted_answer, int(is_correct)),
                    )
                conn.commit()
                result["source"] = "database"
        except DatabaseUnavailable as exc:
            result["source"] = "fallback"
            result["message"] = str(exc)
        return result

    @staticmethod
    def find_exercise(exercise_id):
        for row in ExerciseModel.list_exercises()["data"]:
            if int(row["id"]) == int(exercise_id):
                return row
        return None


def _normalize(row):
    row = dict(row)
    row["options"] = json.loads(row.pop("options_json") or "[]")
    return row

