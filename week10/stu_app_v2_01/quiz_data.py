"""实验平台 —— 概念测验题库

包含4组测验，覆盖DB06全部教学和作业概念：
1. 中间件概念
2. 嵌入式SQL核心概念（SQLCA、共享变量、游标）
3. 存储过程与代码分析
4. 数据管理发展历史
"""


QUIZZES = {
    'middleware': {
        'title': '中间件概念测验',
        'description': '测试对中间件定义、作用和三层架构的理解。',
        'questions': [
            {
                'id': 'q1',
                'type': 'single',
                'question': '什么是中间件（Middleware）？',
                'options': [
                    'A. 操作系统内置的数据库管理模块',
                    'B. 为应用程序访问各类数据库提供统一接口的软件',
                    'C. 数据库厂商提供的专用连接驱动',
                    'D. Web服务器的一种插件'
                ],
                'answer': 'B',
                'explanation': '中间件的核心作用是为上层应用屏蔽底层不同DBMS的差异，提供统一的数据访问接口。'
            },
            {
                'id': 'q2',
                'type': 'multiple',
                'question': '在数据库应用系统中使用中间件有哪些好处？（多选）',
                'options': [
                    'A. 降低学习成本，开发者只需学习统一API',
                    'B. 降低代码耦合，SQL集中在中间层',
                    'C. 便于DBMS迁移，只需修改中间件层',
                    'D. 提升安全性，可统一使用参数化查询防止SQL注入',
                    'E. 自动优化数据库查询性能'
                ],
                'answer': ['A', 'B', 'C', 'D'],
                'explanation': '中间件的好处包括降低学习成本、降低耦合、便于迁移、提升安全性。但中间件本身不自动优化查询性能，查询优化是DBMS的职责。'
            },
            {
                'id': 'q3',
                'type': 'single',
                'question': '本项目中，中间件对应的是哪一部分？',
                'options': [
                    'A. Flask 路由和HTML模板',
                    'B. database.py 中的 Database 类',
                    'C. MySQL 数据库服务器',
                    'D. 浏览器中的JavaScript代码'
                ],
                'answer': 'B',
                'explanation': '本项目的三层架构：表现层(Flask) → 中间件层(Database类) → 数据层(MySQL)。'
            },
            {
                'id': 'q4',
                'type': 'fill',
                'question': '填空：中间件解决的核心问题是应用程序和数据库之间的______问题。',
                'answer': '接口差异',
                'alt_answers': ['接口不统一', '接口不同', '差异性', '差异'],
                'explanation': '不同DBMS提供不同的访问接口，中间件通过统一接口屏蔽了这种差异。'
            },
        ]
    },

    'embedded-sql': {
        'title': '嵌入式SQL核心概念测验',
        'description': '测试对SQLCA、共享变量、游标等嵌入式SQL核心概念的理解。',
        'questions': [
            {
                'id': 'q1',
                'type': 'single',
                'question': 'SQL通信区（SQLCA）的主要作用是什么？',
                'options': [
                    'A. 存储SQL查询返回的数据结果',
                    'B. 向主语言传递SQL语句的执行状态信息',
                    'C. 缓存数据库连接以提高性能',
                    'D. 存储数据库的配置参数'
                ],
                'answer': 'B',
                'explanation': 'SQLCA是结构体变量，用于向主语言传递SQL执行状态（成功/失败、错误码、影响行数等），使主语言能据此控制程序流程。'
            },
            {
                'id': 'q2',
                'type': 'multiple',
                'question': '共享变量在嵌入式SQL中起什么作用？（多选）',
                'options': [
                    'A. 主语言向SQL语句提供参数',
                    'B. 将SQL查询结果传递给主语言进一步处理',
                    'C. 存储SQL语句本身的文本内容',
                    'D. 记录SQL执行耗时用于性能分析'
                ],
                'answer': ['A', 'B'],
                'explanation': '共享变量是双向数据传递的桥梁：主语言→SQL传递参数（如WHERE条件值），SQL→主语言传递查询结果。'
            },
            {
                'id': 'q3',
                'type': 'single',
                'question': '游标（Cursor）主要解决了什么问题？',
                'options': [
                    'A. 数据库连接池的管理问题',
                    'B. SQL集合操作与宿主语言过程操作之间的"阻抗不匹配"',
                    'C. SQL语句的语法解析问题',
                    'D. 多用户并发访问的数据一致性问题'
                ],
                'answer': 'B',
                'explanation': 'SQL是集合操作语言（一次返回多行），宿主语言是过程操作语言（一次处理一行）。游标作为桥梁，将集合结果逐条传递给宿主语言。'
            },
            {
                'id': 'q4',
                'type': 'fill',
                'question': '填空：在C程序的嵌入式SQL中，通过检查 ______ 的值来判断FETCH是否成功。',
                'answer': 'sqlca.sqlcode',
                'alt_answers': ['sqlcode'],
                'explanation': '`if (sqlca.sqlcode != 0) break;` — sqlcode为0表示成功，非0表示遍历结束或出错。'
            },
            {
                'id': 'q5',
                'type': 'fill',
                'question': '填空：`EXEC SQL FETCH SX INTO :S_SID, :S_SName ...` 语句的功能是：将游标指针指向的______读取到共享变量中。',
                'answer': '当前行数据',
                'alt_answers': ['当前行', '一行数据', '数据'],
                'explanation': 'FETCH将游标当前指向的行数据读取到INTO后面的共享变量中，然后游标指针自动下移一行。'
            },
        ]
    },

    'stored-proc': {
        'title': '存储过程与代码分析测验',
        'description': '测试对存储过程优点和嵌入式SQL C程序分析题的理解。',
        'questions': [
            {
                'id': 'q1',
                'type': 'multiple',
                'question': '存储过程相比嵌入式SQL有哪些优点？（多选）',
                'options': [
                    'A. 运行效率高，已编译优化后以二进制形式存储',
                    'B. 降低客户端与服务器之间的通信量',
                    'C. 提升安全性，避免SQL代码外泄和SQL注入',
                    'D. 降低用户交互与数据处理的耦合性',
                    'E. 支持更复杂的数据类型定义'
                ],
                'answer': ['A', 'B', 'C', 'D'],
                'explanation': '存储过程的四大优点：运行效率高、降低通信量、提升安全性、降低耦合性。与数据类型支持无关。'
            },
            {
                'id': 'q2',
                'type': 'single',
                'question': '在嵌入式SQL C程序中，游标SX的作用是什么？',
                'options': [
                    'A. 建立与数据库的网络连接',
                    'B. 存放SQL查询结果集的缓冲区，支持逐行访问',
                    'C. 存储SQL语句的编译版本以提高执行速度',
                    'D. 管理数据库事务的提交和回滚'
                ],
                'answer': 'B',
                'explanation': '游标是存放SQL查询结果集的缓冲区，相当于指向结果集中某条记录的指针，支持逐条访问。'
            },
            {
                'id': 'q3',
                'type': 'single',
                'question': '为什么需要游标？根本原因是什么？',
                'options': [
                    'A. 因为C语言不支持SQL语句的直接执行',
                    'B. 因为SQL返回集合而宿主语言一次只能处理一条记录，存在"阻抗不匹配"',
                    'C. 因为数据库查询结果太多，内存放不下',
                    'D. 因为游标可以自动排序查询结果'
                ],
                'answer': 'B',
                'explanation': '根本原因是SQL的集合操作方式与宿主语言的过程处理方式之间存在不匹配（阻抗不匹配），游标作为桥梁解决这个问题。'
            },
            {
                'id': 'q4',
                'type': 'fill',
                'question': '填空：存储过程通过 ______ 参数接收输入值，通过 ______ 参数返回结果。',
                'answer': 'IN, OUT',
                'alt_answers': ['IN OUT', 'in, out', 'IN,OUT'],
                'explanation': 'IN参数用于传入数据，OUT参数用于返回结果。如本项目的sp_CourseStat：IN p_cid接收课程编号，5个OUT参数返回统计结果。'
            },
        ]
    },

    'history': {
        'title': '数据管理发展历史测验',
        'description': '测试对五个发展阶段及其核心技术、痛点的掌握。',
        'questions': [
            {
                'id': 'q1',
                'type': 'match',
                'question': '将每个发展阶段与其核心技术匹配：',
                'left_items': ['手工管理', '文件系统', 'RDBMS', '大数据/NoSQL', '云原生'],
                'right_items': ['穿孔卡片、磁带', '关系模型、SQL', '键值/文档/列族', '存算分离、Serverless', '磁盘、索引文件'],
                'answer': {'手工管理': '穿孔卡片、磁带', '文件系统': '磁盘、索引文件', 'RDBMS': '关系模型、SQL', '大数据/NoSQL': '键值/文档/列族', '云原生': '存算分离、Serverless'},
                'explanation': '五个阶段的核心技术演进：穿孔卡片→磁盘文件→关系模型→NoSQL→云原生。'
            },
            {
                'id': 'q2',
                'type': 'single',
                'question': '关系型数据库（RDBMS）阶段的"关键飞跃"不包括以下哪项？',
                'options': [
                    'A. ACID（原子性、一致性、隔离性、持久性）保证',
                    'B. 数据的逻辑与物理独立性',
                    'C. 水平扩展（Scale-Out）能力',
                    'D. 标准SQL接口和查询优化器'
                ],
                'answer': 'C',
                'explanation': '水平扩展是NoSQL/大数据阶段解决的核心问题，传统RDBMS在水平扩展方面恰恰是痛点。'
            },
            {
                'id': 'q3',
                'type': 'single',
                'question': 'NoSQL数据库放弃部分ACID主要是为了换取什么？',
                'options': [
                    'A. 更强的数据一致性',
                    'B. 更高的查询灵活性',
                    'C. 高可用与水平扩展能力',
                    'D. 更简单的数据模型设计'
                ],
                'answer': 'C',
                'explanation': 'NoSQL根据CAP定理，放弃强一致性（C），换取可用性（A）和分区容错性（P），从而实现水平扩展。'
            },
            {
                'id': 'q4',
                'type': 'fill',
                'question': '填空：数据库管理技术发展的核心演进逻辑是：程序与数据______ → 声明式操作 → 水平扩展 → 存算分离 + 智能化。',
                'answer': '分离',
                'alt_answers': ['逐步分离', '从绑定到分离'],
                'explanation': '从手工管理的程序数据强绑定，到数据库阶段的完全分离，是数据管理技术发展的核心主线。'
            },
        ]
    }
}


def grade_quiz(quiz_id, user_answers):
    """自动评测验卷

    Args:
        quiz_id: 测验标识符
        user_answers: dict {question_id: user_answer}

    Returns:
        dict: {
            'score': int,
            'total': int,
            'details': [
                {
                    'question_id': str,
                    'correct': bool,
                    'user_answer': ...,
                    'correct_answer': ...,
                    'explanation': str
                }
            ]
        }
    """
    quiz = QUIZZES.get(quiz_id)
    if not quiz:
        return None

    details = []
    correct_count = 0
    total_points = len(quiz['questions'])

    for q in quiz['questions']:
        qid = q['id']
        user_ans = user_answers.get(qid)
        correct = False

        if q['type'] == 'single':
            # 单选：提取选项字母（A/B/C/D）
            user_letter = _extract_letter(user_ans)
            correct = user_letter == q['answer']

        elif q['type'] == 'multiple':
            # 多选：提取所有选项字母，比较集合
            user_set = set(_extract_letters(user_ans) if isinstance(user_ans, str) else user_ans)
            correct_set = set(q['answer'])
            correct = user_set == correct_set

        elif q['type'] == 'fill':
            # 填空：精确匹配或备选答案匹配
            user_text = (user_ans or '').strip()
            correct = user_text == q['answer']
            if not correct and 'alt_answers' in q:
                correct = user_text in q['alt_answers']

        elif q['type'] == 'match':
            # 匹配题：逐对比较
            correct = True
            answer_dict = q['answer']
            if isinstance(user_ans, dict):
                for key, val in answer_dict.items():
                    if user_ans.get(key) != val:
                        correct = False
                        break
            else:
                correct = False

        if correct:
            correct_count += 1

        details.append({
            'question_id': qid,
            'correct': correct,
            'user_answer': user_ans,
            'correct_answer': q['answer'],
            'explanation': q.get('explanation', ''),
            'question_text': q['question']
        })

    score = int(correct_count / total_points * 100) if total_points > 0 else 0

    return {
        'score': score,
        'total': total_points,
        'correct_count': correct_count,
        'details': details
    }


def _extract_letter(text):
    """从选项文本中提取字母（A/B/C/D）"""
    if not text:
        return ''
    text = text.strip()
    if text and text[0].upper() in 'ABCDE':
        return text[0].upper()
    return text.upper()


def _extract_letters(text):
    """从多选答案中提取所有字母"""
    if not text:
        return []
    letters = []
    for char in text.upper():
        if char in 'ABCDE':
            letters.append(char)
    return letters
