import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="p5动画案例", page_icon="🎬", layout="wide")

st.header("🎬 p5.js 动画案例")
st.markdown("这些动画对应 Markdown 课件的核心图：数据块、定长/变长记录、B+树、哈希索引、位图索引。学生可以直接调参数看变化。")


def p5_html(sketch_js, height=430):
    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.9.4/p5.min.js"></script>
  <style>
    body {{ margin:0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background:#ffffff; }}
    .note {{ font-size:14px; color:#333; padding:8px 0; }}
  </style>
</head>
<body>
<script>
{sketch_js}
</script>
</body>
</html>
"""
    components.html(html, height=height, scrolling=False)


tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "按块读取",
    "定长/变长",
    "B+树范围查询",
    "哈希桶冲突",
    "位图 AND",
])

with tab1:
    st.subheader("数据库为什么按块读取？")
    block_size = st.slider("每个块放几条记录", 3, 8, 4, key="p5_block_size")
    target = st.slider("查询第几条记录", 1, 32, 17, key="p5_target_record")
    p5_html(f"""
let blockSize = {block_size};
let target = {target};
function setup() {{
  createCanvas(900, 360);
  textFont('Arial');
}}
function draw() {{
  background(255);
  fill(30); textSize(20); text('按块读取：查询一条记录，也要把所在数据块读进内存', 20, 32);
  let targetBlock = floor((target - 1) / blockSize);
  let x0 = 40, y0 = 80, bw = 150, bh = 180, gap = 24;
  for (let b = 0; b < 6; b++) {{
    let x = x0 + b * (bw + gap);
    stroke(b === targetBlock ? '#d32f2f' : '#777');
    strokeWeight(b === targetBlock ? 4 : 1.5);
    fill(b === targetBlock ? '#ffebee' : '#f6f8fa');
    rect(x, y0, bw, bh, 8);
    noStroke(); fill(30); textSize(15); text('数据块 ' + (b + 1), x + 42, y0 + 24);
    for (let i = 0; i < blockSize; i++) {{
      let rec = b * blockSize + i + 1;
      let ry = y0 + 44 + i * (120 / blockSize);
      fill(rec === target ? '#ff9800' : '#90caf9');
      rect(x + 20, ry, bw - 40, 18, 4);
      fill(0); textSize(12); text('记录 ' + rec, x + 52, ry + 13);
    }}
  }}
  fill('#d32f2f'); textSize(18);
  text('目标记录 ' + target + ' 在第 ' + (targetBlock + 1) + ' 块，所以读取整个块。', 40, 310);
}}
""")
    st.caption("学生观察：把目标记录从 1 拖到 32，看红色数据块如何变化。")

with tab2:
    st.subheader("定长记录 vs 变长记录")
    name_len = st.slider("姓名长度", 2, 20, 6, key="p5_name_len")
    addr_len = st.slider("地址长度", 10, 100, 35, key="p5_addr_len")
    p5_html(f"""
let nameLen = {name_len};
let addrLen = {addr_len};
function setup() {{ createCanvas(900, 360); textFont('Arial'); }}
function field(x, y, w, label, color) {{
  fill(color); stroke('#555'); rect(x, y, w, 44, 5);
  noStroke(); fill(0); textSize(13); text(label, x + 8, y + 27);
}}
function draw() {{
  background(255);
  fill(30); textSize(20); text('定长像宿舍床位：不管人多瘦，都给固定床；变长像行李箱：按实际大小放。', 20, 32);
  textSize(17); fill(20); text('定长记录：固定 10B + 20B + 2B + 100B', 40, 82);
  field(40, 105, 80, '学号10B', '#bbdefb');
  field(120, 105, 130, '姓名20B', '#c8e6c9');
  field(250, 105, 55, '性别2B', '#ffe0b2');
  field(305, 105, 300, '地址100B', '#ffcdd2');
  fill('#d32f2f'); noStroke(); text('空白也要占位置，查找快但可能浪费空间', 620, 133);

  textSize(17); fill(20); text('变长记录：10B + 实际姓名 + 2B + 实际地址', 40, 205);
  field(40, 228, 80, '学号10B', '#bbdefb');
  field(120, 228, nameLen * 7, '姓名' + nameLen + 'B', '#c8e6c9');
  field(120 + nameLen * 7, 228, 55, '性别2B', '#ffe0b2');
  field(175 + nameLen * 7, 228, addrLen * 3, '地址' + addrLen + 'B', '#ffcdd2');
  fill('#2e7d32'); text('节省空间，但要靠长度/偏移量定位', 620, 256);
}}
""")

with tab3:
    st.subheader("B+树范围查询：先定位，再沿叶子链表扫")
    start = st.slider("范围起点", 5, 85, 25, step=5, key="p5_btree_start")
    end = st.slider("范围终点", 10, 95, 75, step=5, key="p5_btree_end")
    if start > end:
        start, end = end, start
    p5_html(f"""
let startKey = {start};
let endKey = {end};
let leaves = [[1,5,10,15],[20,25,30,35],[50,55,60,65],[80,85,90,95]];
function setup() {{ createCanvas(900, 400); textFont('Arial'); }}
function drawNode(x,y,w,h,label,hot) {{
  stroke(hot ? '#d32f2f' : '#555'); strokeWeight(hot ? 4 : 1.5);
  fill(hot ? '#ffebee' : '#e3f2fd'); rect(x,y,w,h,8);
  noStroke(); fill(0); textAlign(CENTER,CENTER); textSize(15); text(label,x+w/2,y+h/2);
}}
function draw() {{
  background(255); textAlign(LEFT,BASELINE);
  fill(30); textSize(20); text('B+树范围查询：SELECT ... WHERE Sno BETWEEN ' + startKey + ' AND ' + endKey, 20, 32);
  drawNode(410,65,80,42,'50', false);
  drawNode(250,135,80,42,'20', false); drawNode(570,135,80,42,'80', false);
  stroke('#777'); line(450,107,290,135); line(450,107,610,135);
  let x0=80, y=235, w=150, h=58;
  for(let i=0;i<leaves.length;i++) {{
    let arr=leaves[i];
    let hot = arr.some(v => v>=startKey && v<=endKey);
    drawNode(x0+i*(w+35), y, w, h, arr.join(' | '), hot);
    if(i<leaves.length-1) {{ stroke('#2e7d32'); strokeWeight(3); line(x0+i*(w+35)+w, y+h/2, x0+(i+1)*(w+35), y+h/2); }}
  }}
  fill('#2e7d32'); noStroke(); textSize(17); text('绿色链表让范围查询不用回到根节点反复查。', 80, 340);
}}
""")

with tab4:
    st.subheader("哈希索引：等值快，范围不行")
    bucket_count = st.slider("桶数量", 3, 10, 5, key="p5_hash_buckets")
    keys = [10086, 10096, 10106, 20123, 30111, 40121, 50131]
    p5_html(f"""
let bucketCount = {bucket_count};
let keys = {keys};
function setup() {{ createCanvas(900, 390); textFont('Arial'); }}
function draw() {{
  background(255);
  fill(30); textSize(20); text('哈希函数：bucket = key % ' + bucketCount, 20, 32);
  let bx=70, by=80, bw=90, bh=210, gap=18;
  for(let b=0;b<bucketCount;b++) {{
    fill('#f6f8fa'); stroke('#555'); strokeWeight(1.5); rect(bx+b*(bw+gap),by,bw,bh,8);
    noStroke(); fill(0); textAlign(CENTER); textSize(14); text('桶 '+b,bx+b*(bw+gap)+bw/2,by+24);
  }}
  let slots = Array(bucketCount).fill(0);
  for(let i=0;i<keys.length;i++) {{
    let k=keys[i], b=k%bucketCount;
    let x=bx+b*(bw+gap)+12, y=by+45+slots[b]*28;
    fill(slots[b]===0 ? '#bbdefb' : '#ffcc80');
    stroke('#777'); rect(x,y,bw-24,22,4);
    noStroke(); fill(0); textAlign(CENTER); textSize(12); text(k,x+(bw-24)/2,y+16);
    slots[b]++;
  }}
  textAlign(LEFT); fill('#d32f2f'); textSize(16);
  text('同一个桶里多条记录就是冲突，需要桶内查找或挂溢出链。范围查询会被打散。', 70, 340);
}}
""")

with tab5:
    st.subheader("位图索引：低基数字段用位运算")
    p5_html("""
let names = ['张三','李四','王五','赵六','钱七'];
let male = [1,0,1,0,1];
let db = [1,0,0,1,1];
function setup() { createCanvas(900, 360); textFont('Arial'); }
function drawBits(arr, y, label, color) {
  fill(30); noStroke(); textSize(16); text(label, 50, y+28);
  for(let i=0;i<arr.length;i++) {
    fill(arr[i] ? color : '#eeeeee'); stroke('#777'); rect(180+i*80, y, 48, 48, 6);
    noStroke(); fill(0); textAlign(CENTER,CENTER); textSize(18); text(arr[i], 204+i*80, y+24);
    textSize(12); text(names[i], 204+i*80, y+66);
  }
  textAlign(LEFT,BASELINE);
}
function draw() {
  background(255);
  fill(30); textSize(20); text('位图 AND：查询“男生 且 选了数据库课”', 20, 32);
  drawBits(male, 75, '性别=男', '#bbdefb');
  drawBits(db, 155, '课程=数据库', '#c8e6c9');
  let result = male.map((v,i)=>v & db[i]);
  drawBits(result, 235, 'AND结果', '#ffcc80');
  fill('#2e7d32'); textSize(16); text('结果中 1 的位置就是满足条件的记录。', 600, 265);
}
""")

st.divider()
st.subheader("课堂使用建议")
st.markdown("""
1. 先在本页看动画，回答“为什么”。
2. 再到 `EXPLAIN分析工具`、`任务1`、`任务2` 页面跑真实 SQL。
3. 最后把观察到的 `type`、`key`、`rows` 写进实验报告。
""")
