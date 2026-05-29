import pandas as pd
import streamlit as st


st.set_page_config(page_title="索引结构互动演示", page_icon="🧭", layout="wide")

st.header("🧭 索引结构互动演示")
st.markdown("用学生表、图书目录和快递分拣这类日常案例，理解课件里的各种索引。")


students = [
    {"Sno": 20180001, "Name": "李明", "Gender": "男", "Major": "数据科学", "Block": 1},
    {"Sno": 20180002, "Name": "王芳", "Gender": "女", "Major": "计算机科学", "Block": 1},
    {"Sno": 20180003, "Name": "赵强", "Gender": "男", "Major": "信息安全", "Block": 1},
    {"Sno": 20180004, "Name": "刘敏", "Gender": "女", "Major": "软件工程", "Block": 2},
    {"Sno": 20180005, "Name": "陈晨", "Gender": "女", "Major": "计算机科学", "Block": 2},
    {"Sno": 20180006, "Name": "周杰", "Gender": "男", "Major": "信息管理", "Block": 2},
    {"Sno": 20180007, "Name": "吴迪", "Gender": "男", "Major": "数据科学", "Block": 3},
    {"Sno": 20180008, "Name": "孙娜", "Gender": "女", "Major": "计算机科学", "Block": 3},
    {"Sno": 20180009, "Name": "郑凯", "Gender": "男", "Major": "信息安全", "Block": 3},
    {"Sno": 20180010, "Name": "冯雪", "Gender": "女", "Major": "软件工程", "Block": 4},
    {"Sno": 20180011, "Name": "高磊", "Gender": "男", "Major": "数据科学", "Block": 4},
    {"Sno": 20180012, "Name": "黄蓉", "Gender": "女", "Major": "信息管理", "Block": 4},
    {"Sno": 20180013, "Name": "马超", "Gender": "男", "Major": "计算机科学", "Block": 5},
    {"Sno": 20180014, "Name": "罗兰", "Gender": "女", "Major": "信息安全", "Block": 5},
    {"Sno": 20180015, "Name": "何平", "Gender": "男", "Major": "软件工程", "Block": 5},
]


def student_by_sno(sno):
    return next((s for s in students if s["Sno"] == sno), None)


def dense_steps(sno):
    found = student_by_sno(sno)
    steps = [
        "稠密索引像每个学生都有一张目录卡片。",
        f"在索引中二分查找学号 {sno}。",
    ]
    if found:
        steps.append(f"索引项直接指向第 {found['Block']} 块中的记录。")
    else:
        steps.append("索引中没有该学号，所以记录不存在。")
    return steps


def sparse_steps(sno):
    block_heads = [s for s in students if s["Sno"] % 3 == 1]
    target_block = None
    for head in block_heads:
        if sno >= head["Sno"]:
            target_block = head["Block"]
    steps = [
        "稀疏索引像每个书架只贴第一本书的标签。",
        "先在块首索引中找到最接近且不大于目标学号的块首记录。",
    ]
    if target_block:
        steps.append(f"定位到第 {target_block} 块，再在块内顺序查找。")
        found = student_by_sno(sno)
        steps.append("找到记录。" if found else "块内没有该学号，记录不存在。")
    else:
        steps.append("目标比第一块首记录还小，记录不存在。")
    return steps


def hash_bucket(sno, bucket_count):
    return sno % bucket_count


df_students = pd.DataFrame(students)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "顺序索引",
    "辅助索引",
    "B+树",
    "哈希索引",
    "位图索引",
])

with tab1:
    st.subheader("稠密、稀疏、多级索引")
    st.markdown("案例：学生表按学号有序存放，每个磁盘块放 3 条记录。")
    st.dataframe(df_students, use_container_width=True, hide_index=True)

    query_sno = st.select_slider("选择要查询的学号", options=[s["Sno"] for s in students], value=20180013)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**稠密索引**")
        dense = pd.DataFrame({"Sno": [s["Sno"] for s in students], "Pointer": [f"块{s['Block']}:{s['Name']}" for s in students]})
        st.dataframe(dense, use_container_width=True, hide_index=True)
        for step in dense_steps(query_sno):
            st.write(step)

    with c2:
        st.markdown("**稀疏索引**")
        sparse = pd.DataFrame({"块首 Sno": [s["Sno"] for s in students if s["Sno"] % 3 == 1], "Block": [s["Block"] for s in students if s["Sno"] % 3 == 1]})
        st.dataframe(sparse, use_container_width=True, hide_index=True)
        for step in sparse_steps(query_sno):
            st.write(step)

    st.markdown("**多级索引**")
    st.info("当一级索引本身也很大时，再给索引建立上层目录。就像图书馆先查楼层目录，再查书架目录，最后找书。")
    st.code("""
顶层索引: [20180001, 20180010]
  ├─ 二级索引 A: [20180001, 20180004, 20180007]
  └─ 二级索引 B: [20180010, 20180013]
       └─ 数据块: 20180013, 20180014, 20180015
""")

with tab2:
    st.subheader("辅助索引与指针桶")
    st.markdown("辅助索引建在非排序字段上。因为表没有按专业排序，所以同一个专业的记录可能散落在多个块中。")
    major = st.selectbox("选择专业", sorted(df_students["Major"].unique()))
    bucket = df_students[df_students["Major"] == major][["Sno", "Name", "Block"]]
    st.markdown(f"专业 `{major}` 的指针桶：")
    st.dataframe(bucket, use_container_width=True, hide_index=True)
    st.success("查询时先找到专业索引项，再拿到指针桶，最后按指针去不同数据块取记录。")

    st.markdown("**复合条件查询：专业 + 性别**")
    gender = st.radio("性别", ["男", "女"], horizontal=True)
    major_set = set(df_students[df_students["Major"] == major]["Sno"])
    gender_set = set(df_students[df_students["Gender"] == gender]["Sno"])
    result = df_students[df_students["Sno"].isin(major_set & gender_set)]
    st.write(f"专业指针集合 ∩ 性别指针集合 = {sorted(major_set & gender_set)}")
    st.dataframe(result, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("B+树：为什么范围查询快")
    order = st.slider("B+树阶数（每个结点最多指针数）", 3, 6, 4)
    leaf_size = order - 1
    leaves = [students[i:i + leaf_size] for i in range(0, len(students), leaf_size)]
    st.markdown("叶子结点保存真正的索引项，并且从左到右串成链表。")
    leaf_labels = ["[" + ", ".join(str(s["Sno"])[-2:] for s in leaf) + "]" for leaf in leaves]
    st.code("  ->  ".join(leaf_labels))

    start = st.select_slider("范围起点", options=[s["Sno"] for s in students], value=20180008)
    end = st.select_slider("范围终点", options=[s["Sno"] for s in students], value=20180013)
    if start > end:
        start, end = end, start
    matched = df_students[(df_students["Sno"] >= start) & (df_students["Sno"] <= end)]
    st.write(f"先从根结点一路找到 `{start}` 所在叶子，再沿叶子链表向右扫到 `{end}`。")
    st.dataframe(matched, use_container_width=True, hide_index=True)

    st.markdown("**维护演示**")
    op = st.radio("操作", ["插入", "删除"], horizontal=True)
    if op == "插入":
        st.info("插入新 key 时，先找到叶子结点。有空位就直接插入；满了就分裂叶子，并把分裂点提升到父结点。")
    else:
        st.info("删除 key 后，如果叶子结点太空，就向兄弟借 key；借不到就合并，并同步维护父结点。")

with tab4:
    st.subheader("哈希索引：快递分拣式等值查询")
    st.markdown("哈希函数像快递分拣规则：看编号，直接投到某个桶。")
    bucket_count = st.slider("哈希桶数量", 3, 8, 4)
    buckets = {}
    for s in students:
        buckets.setdefault(hash_bucket(s["Sno"], bucket_count), []).append(s)

    bucket_df = pd.DataFrame([
        {"桶号": b, "索引项": ", ".join(str(x["Sno"])[-2:] for x in rows), "数量": len(rows)}
        for b, rows in sorted(buckets.items())
    ])
    st.dataframe(bucket_df, use_container_width=True, hide_index=True)

    lookup = st.select_slider("等值查询学号", options=[s["Sno"] for s in students], value=20180014)
    b = hash_bucket(lookup, bucket_count)
    st.success(f"h({lookup}) = {lookup} % {bucket_count} = {b}，直接去 {b} 号桶查。")
    st.warning("哈希索引不适合 `Sno >= 20180009` 这种范围查询，因为相邻学号可能被分到不同桶。")

with tab5:
    st.subheader("位图索引：适合低基数字段")
    st.markdown("性别、是否毕业、部门类别这类取值很少的字段，可以用 0/1 位向量表示。")
    bitmap_rows = []
    for _, row in df_students.iterrows():
        bitmap_rows.append({
            "Sno": row["Sno"],
            "Name": row["Name"],
            "男": 1 if row["Gender"] == "男" else 0,
            "女": 1 if row["Gender"] == "女" else 0,
            "计算机科学": 1 if row["Major"] == "计算机科学" else 0,
            "信息安全": 1 if row["Major"] == "信息安全" else 0,
        })
    bitmap_df = pd.DataFrame(bitmap_rows)
    st.dataframe(bitmap_df, use_container_width=True, hide_index=True)

    st.markdown("实验：统计“计算机科学专业女生”。")
    selected = bitmap_df[(bitmap_df["女"] & bitmap_df["计算机科学"]) == 1]
    st.write("女 位图 AND 计算机科学 位图，结果中 1 的个数就是人数。")
    st.metric("人数", len(selected))
    st.dataframe(selected[["Sno", "Name"]], use_container_width=True, hide_index=True)

st.divider()
st.subheader("学生实验")
st.markdown("""
1. 分别用稠密索引、稀疏索引描述查询 `20180014` 的过程。
2. 用 B+树说明为什么 `BETWEEN 20180008 AND 20180013` 不需要逐块全表扫描。
3. 调整哈希桶数量，观察桶溢出风险如何变化。
4. 用位图索引解释“统计女生人数”为什么可以不访问基本表。
""")
