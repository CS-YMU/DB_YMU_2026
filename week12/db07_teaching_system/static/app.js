// ==================== 课程主题数据（增强版） ====================
const topics = [
  {
    id: "problem",
    title: "1. 为什么要规范化",
    subtitle: "从冗余和异常看表设计问题",
    source: "对应课件 7.1",
    summary: "一张表如果同时塞进学生、课程、教师等多种主题，就会出现重复数据和维护麻烦。规范化的第一步不是背定义，而是看清楚一张表到底混了几件事。",
    keyPoints: [
      "外延 vs 内涵：外延是杯子里实际装的水（当前数据，随时在变）；内涵是杯子的形状和容量（表结构和约束，相对稳定）。",
      "三种异常：修改异常（改一处需改多处，像改一个错别字要翻遍整本书）、插入异常（缺主键无法插入，像没有学生选课就开不了课）、删除异常（删数据连带丢信息，像删学生记录把课程信息也删了）。",
      "非形式化准则：一事一地、减少空值、避免异常、规范连接（主键-外键连接）。",
      "数据冗余和操作异常的根源是：一个关系模式中混合了多个不同主题的信息。",
    ],
    analogy: "像把学生档案、课程档案、选课记录写在同一张纸上。查起来看似方便，但一改课程名就要到处改，漏一处就错一处。",
    caseTitle: "学生选课表 — 经典反例",
    caseBody: "R(S#, C#, CName, TName)。如果 C# 可以决定 CName 和 TName，那么课程信息会随每个选课学生重复出现。新开课程（如C++）还没人选课时，因缺少S#无法插入。更合理的做法是拆成 选课(S#, C#) 和 课程(C#, CName, TName)。",
    teacherTip: "先展示异常现象，让学生产生'这表设计有问题'的直觉，再引出函数依赖的概念。学生理解'为什么拆表'后，后面的范式定义会轻很多。",
    commonMistakes: [
      "误区：当前表里没有重复数据，就认为设计没问题。→ 异常不一定在当前数据中显现。",
      "误区：把所有信息放一张表查询方便。→ 短期方便，长期维护灾难。",
    ],
    toolLink: null,
  },
  {
    id: "fd",
    title: "2. 函数依赖与推理",
    subtitle: "用业务规则表达属性之间的确定关系",
    source: "对应课件 7.2.1-7.2.4",
    summary: "函数依赖 X→Y 表示只要 X 的值相同，Y 的值就必须相同。它来自业务语义，而不是只看当前几行数据。FD 分为'平凡'和'非平凡'两大类：右边的属性被左边包住的（平凡），是废话，永远成立；右边跑出左边的（非平凡），才是真正要管的业务约束。",
    keyPoints: [
      "X→Y 的通俗说法：X 能唯一确定 Y。任意两个元组若在 X 上相等，则在 Y 上也必须相等。",
      "平凡 FD：右边 ⊆ 左边（如 (学号,姓名)→学号），废话一句，永远成立，规范化直接忽略。",
      "非平凡 FD：右边至少有一个属性不在左边（如 学号→姓名），这才是核心关注对象，可能产生冗余和异常。",
      "完全非平凡 FD：左右无交集（如 学号→系名），是最典型的非平凡依赖。",
      "不能仅凭当前数据没有反例就断定 FD 成立——当前实例只能用来找反例（证伪），不能用来证明。",
      "自反律 A1（废话生成器）：知道整体一定知道部分。如知道{学号,姓名}当然知道{学号}。平凡依赖的来源。",
      "增广律 A2（两边加衣服）：X→Y 则 XZ→YZ。如学号→姓名，那么(学号,课程号)→(姓名,课程号)。",
      "传递律 A3（链条传递）：X→Y 且 Y→Z 则 X→Z。如学号→系号→系主任，所以学号→系主任。3NF要消除的就是这种链条。",
      "合并律 A4：X→Y 且 X→Z 则 X→YZ。知道学号能查姓名，也知道学号能查年龄，那学号就能一起查出(姓名,年龄)。",
      "分解律 A5：X→YZ 则 X→Y 且 X→Z。知道学号能查(姓名,年龄)，那学号当然也能单独查姓名。",
      "伪传递律 A6：X→Y 且 WY→Z 则 WX→Z。如学号→姓名，(姓名,课程)→成绩，则(学号,课程)→成绩。",
      "复合律 A7：X→Y 且 W→Z 则 XW→YZ。两条独立的决定关系可以并排组合。",
    ],
    analogy: "平凡依赖就像说'你和你自己长得一样'——绝对是废话。非平凡依赖才是'身份证号能查出你的出生日期'——这才是真正有用的规则。所以判断口诀：右边被左边包住的，废话；右边跑出左边的，才要管。",
    caseTitle: "平凡 vs 非平凡 — 一眼分清的技巧",
    caseBody: "核心判断：看右边的属性集是不是左边的子集。平凡 FD（Y⊆X）：(学号,课程号)→学号、(学号,姓名)→姓名——右边全在左边里，永远成立。非平凡 FD（Y⊈X）：学号→姓名、课程号→学分——右边至少有一个不在左边，要依据业务规则判定。完全非平凡 FD（X∩Y=∅）：学号→系名——左右毫无交集，最典型。一句话记忆：右边被左边包住的，废话；右边跑出左边的，才要管。",
    teacherTip: "强调'函数依赖是对所有合法数据都成立'。让学生一条条分析'谁决定谁'，重点区分单属性决定和多属性组合决定。讲解平凡/非平凡时，可以让学生自己举几个'废话依赖'的例子（如AB→A），体会为什么规范化只关心非平凡FD。",
    commonMistakes: [
      "误区：把'当前表中X列值都不同'当作X→Y成立。→ FD 必须基于业务规则。",
      "误区：混淆相关性和函数依赖。→ '身高和体重相关'不是FD，因为同一身高可能对应不同体重。",
      "误区：认为平凡 FD 也需要业务规则支撑。→ 平凡 FD 纯粹由集合包含关系保证，永远成立。",
    ],
    toolLink: "closure",
  },
  {
    id: "closure",
    title: "3. 闭包、候选键与最小依赖集",
    subtitle: "把推理变成可计算的步骤",
    source: "对应课件 7.2.5-7.2.7",
    summary: "属性闭包 X⁺ 是从 X 出发，根据函数依赖能推出的全部属性。它可以用来判断超键（X⁺=U）、候选键（极小超键），也能辅助求最小依赖集（去掉冗余依赖和冗余属性）。",
    keyPoints: [
      "超键 vs 候选键：超键是能打开所有门的钥匙串（可能有多余的钥匙）。候选键是刚好够用的最小钥匙串——多一把都是浪费。",
      "闭包算法：反复扫描 F，找到左部已在当前闭包中的依赖，将右部加入闭包，直到收敛。",
      "最小依赖集三步法：①右部单属性化（把多功能钥匙拆成单功能）②消冗余依赖（两把能开同一扇门的钥匙，扔掉一把）③消左部冗余属性（钥匙上有三个齿，其实两个就够了）。",
      "两个 FD 集等价 ⇔ 它们的闭包 F⁺ = G⁺。最小依赖集是与原集等价的、最简洁的表示。",
    ],
    analogy: "闭包像一串钥匙：你手里先有 A，A 能打开 B 的锁，拿到 B 后又发现 B 能打开 C 的锁……不断把新钥匙串到钥匙圈上，直到没有新锁能打开为止。",
    caseTitle: "闭包计算与最小覆盖示例",
    caseBody: "F={A→B, B→C, C→D, CD→E, E→F}。A⁺ 从 {A} 开始：A→B 得 B，B→C 得 C，C→D 得 D，加上 C 后 CD→E 得 E，E→F 得 F。最终 A⁺={A,B,C,D,E,F}=U，所以 A 是候选键。",
    teacherTip: "让学生每次只问一个问题：当前手里的属性能触发哪条 FD？这样闭包计算不会乱。候选键求解从单属性开始逐一检查，找到 CK 后包含它的组合直接跳过。",
    commonMistakes: [
      "误区：求候选键时忘记检查极小性。→ 超键不一定是候选键，需确认无真子集也是超键。",
      "误区：最小依赖集不唯一。→ 不同消除顺序可能得到不同的最小覆盖，但它们都等价。",
    ],
    toolLink: "closure",
  },
  {
    id: "decomposition",
    title: "4. 模式分解：无损与保持依赖",
    subtitle: "拆表不能丢信息，也要尽量保留约束",
    source: "对应课件 7.3",
    summary: "分解不是随便拆。好的分解需要自然连接后能恢复原来的信息（无损连接），还要尽量让原有函数依赖可以在子表中直接检查（保持依赖）。Chase 过程是判断无损连接的系统性算法。",
    keyPoints: [
      "无损连接：分解后的表自然连接 = 原关系，不丢失信息也不产生寄生元组。像拆拼图，拼回去必须和原图一模一样。",
      "保持依赖：原来的函数依赖可由各子模式上的投影依赖的并集逻辑蕴涵。像搬家，新家也要能执行原来的 house rules。",
      "二模式分解无损判定：若公共属性是其中一个子模式的超键，则分解无损。",
      "Chase 过程：像拼图填色游戏。每个子表一开始只知道自己那块，其他位置是问号。用 FD 规则不断把问号变成确定图案，最后看能不能拼出完整的一行。",
      "四种组合比喻：无损+保持=拼图完整且规则都在（理想）；无损+不保持=拼图完整但有些规则要跨屋检查（可接受）；有损+保持=拼图多了一块假的（不可接受）；有损+不保持=拼图多了假的且规则也丢了（最差）。",
    ],
    analogy: "拆一份合同成几页可以，但重新装订后内容必须完整，不能多出一条双方都没签过的条款。同时，原来合同的约束（如'签字人必须是法人'）在新分页中也要能检查。",
    caseTitle: "订单表拆分与 Chase 判定",
    caseBody: "R(ABCD)，F={B→A, C→D}，分解 ρ={AB, BC, CD}。Chase 过程：初始表 R1(a1,a2,b13,b14), R2(b21,a2,a3,b24), R3(b31,b32,a3,a4)。应用 B→A：R1和R2在B列同为a2，将R2的A列改为a1。应用 C→D：R2和R3在C列同为a3，将R2的D列改为a4。此时 R2=(a1,a2,a3,a4) 全a，判定无损！",
    teacherTip: "课堂上可以先让学生提出拆法，再用'能不能还原'和'约束在哪里检查'两个问题检验。Chase 过程建议用板书逐步演示，动画效果尤佳。",
    commonMistakes: [
      "误区：分解的子表越多越好。→ 过多会导致查询连接复杂、性能下降。",
      "误区：只要公共属性是主键就无损。→ 必须是其中一个子模式的超键，不是原模式的超键。",
    ],
    toolLink: "chase",
  },
  {
    id: "normal_forms",
    title: "5. 范式：1NF 到 5NF",
    subtitle: "用分级标准评价表设计质量",
    source: "对应课件 7.4-7.6",
    summary: "范式是关系模式设计质量的分级标准。1NF→2NF→3NF→BCNF 逐级消除函数依赖导致的问题，4NF 处理多值依赖，5NF 处理连接依赖。教学和应用重点是 3NF 与 BCNF。",
    keyPoints: [
      "1NF（属性不可再分）：像快递地址不能写'北京市海淀区'混在一个格子里，必须拆成省、市、区，否则没法按市统计。",
      "2NF（消除部分依赖）：像学生证上印了学号、姓名、班级、班主任。但班主任其实只由班级决定，不是由学号直接决定。把班主任信息拆到班级表。",
      "3NF（消除传递依赖）：像员工档案里，员工→部门→部门经理。部门经理传递依赖于员工，应该拆到部门表里。",
      "BCNF（决定因素必是超键）：比 3NF 更严格——任何一个决定因素都必须能唯一标识整行。像课程表，如果'教室→容量'且教室不是超键，就不满足 BCNF。分解时可能丢失依赖。",
      "4NF（消除多值依赖）：像课程-学生-先修课。学生和先修课各自独立地'多对一'于课程，却被迫做笛卡尔积（2学生×3先修课=6行）。拆成两个表就不冗余了。",
      "5NF（消除连接依赖）：像供应商-零件-项目三元关系。强行拆成三个二元关系会产生'凭空多出一行'的连接陷阱。保持三元关系才是 5NF。",
      "工程权衡：规范化不是越高越好。实际系统以 3NF/BCNF 为目标，必要时为查询效率做受控反规范化。",
    ],
    analogy: "范式像体检指标：1NF 是'能走路'，2NF 是'血压正常'，3NF 是'血脂正常'，BCNF 是'全部指标优秀'。但 BCNF 也不保证没有健康隐患（MVD 问题），需要 4NF 进一步检查。不是指标越高越适合所有系统——职业运动员（高频查询系统）可能需要适度牺牲某些指标换取性能。",
    caseTitle: "范式升级路径演示",
    caseBody: "从一张混合表 R(S#,C#,Score,T#,Title) 开始：①确保原子化→1NF；②消除部分依赖(T#,Title只依赖C#)→2NF，拆出课程-教师表；③消除传递依赖(C#→T#→Title)→3NF，再拆出教师表；④检查BCNF，确认所有FD左部都是超键。最终三个表：选课(S#,C#,Score)、课程(C#,T#)、教师(T#,Title)。",
    teacherTip: "最后强调工程权衡：实际系统常以 3NF/BCNF 为目标，必要时为了查询效率做受控反规范化。可以展示一个实际电商系统的表结构来说明'适度冗余'的合理性。",
    commonMistakes: [
      "误区：范式越高越好，全部拆到 5NF。→ 表太多连接开销大，实际 3NF/BCNF 即可。",
      "误区：满足 BCNF 就完全没有冗余了。→ 还有 MVD 导致的冗余（如课程-学生-先修课案例）。",
    ],
    toolLink: "normform",
  },
];

// ==================== 工具预设数据 ====================
const toolPresets = {
  closure: [
    { label: "示例1：A+ → 全部属性", x: "A", fds: "A→B\nB→C\nC→D\nCD→E\nE→F" },
    { label: "示例2：(AD)+ → 全部属性", x: "AD", fds: "A→B\nB→C\nD→B" },
    { label: "示例3：(AB)+ → ABC", x: "AB", fds: "A→B\nB→C" },
    { label: "示例4：A+ → 只有自己", x: "A", fds: "AB→C\nC→D" },
  ],
  keys: [
    { label: "示例1：单属性候选键", attrs: "A,B,C,D,E,F", fds: "A→B\nB→C\nC→D\nCD→E\nE→F" },
    { label: "示例2：复合候选键", attrs: "A,B,C,D,E", fds: "A→B\nC→D" },
    { label: "示例3：物流订单表", attrs: "OID,PID,CID,CName,PName,Qty,WID,WAddr,DDate", fds: "OID→CID\nOID→DDate\nCID→CName\nPID→PName\nWID→WAddr\nOIDPID→Qty\nOIDPID→WID" },
  ],
  mincover: [
    { label: "示例1：经典案例 A→BC", fds: "A→BC\nB→C\nA→B\nAB→C" },
    { label: "示例2：含左部冗余属性", fds: "AB→C\nA→B\nB→C\nC→D" },
    { label: "示例3：教师职称工资", fds: "T#→Title\nTitle→Salary\nT#→Salary" },
  ],
  normform: [
    { label: "示例1：R(ABC), A→B, B→C → 2NF", attrs: "A,B,C", fds: "A→B\nB→C" },
    { label: "示例2：R(ABCDE), A→B, C→D → 1NF", attrs: "A,B,C,D,E", fds: "A→B\nC→D" },
    { label: "示例3：教师工资 → 2NF", attrs: "T#,Title,Salary", fds: "T#→Title\nTitle→Salary" },
    { label: "示例4：课程-学生-先修课 → BCNF", attrs: "C#,S#,PreC#", fds: "" },
  ],
  chase: [
    { label: "示例1：无损分解 ρ={AB,BC,CD}", attrs: "A,B,C,D", fds: "B→A\nC→D", decomp: "AB\nBC\nCD" },
    { label: "示例2：有损分解 ρ={AB,ACD}", attrs: "A,B,C,D", fds: "A→B\nC→D", decomp: "AB\nACD" },
    { label: "示例3：二模式无损判定", attrs: "A,B,C,D", fds: "A→BCD", decomp: "AB\nACD" },
  ],
};

// ==================== 全局状态 ====================
let activeTopic = topics[0].id;
let teacherMode = localStorage.getItem("teacherMode") === "1";
let completed = new Set(JSON.parse(localStorage.getItem("completedTopics") || "[]"));
let exercisesByTopic = {};
let exerciseSource = "loading";
let currentCaseId = null;

// ==================== 渲染函数 ====================

function renderNav() {
  const nav = document.querySelector("#topicNav");
  nav.innerHTML = topics.map(topic => `
    <button class="${topic.id === activeTopic ? "active" : ""}" data-topic="${topic.id}">
      <span>${topic.title}</span>
      <small>${topic.subtitle}</small>
    </button>
  `).join("");
  nav.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", () => {
      activeTopic = btn.dataset.topic;
      completed.add(activeTopic);
      saveProgress();
      renderAll();
    });
  });
}

function renderOverview() {
  document.querySelector("#overview").innerHTML = topics.map(topic => `
    <button class="overview-item ${topic.id === activeTopic ? "active" : ""}" data-topic="${topic.id}">
      <strong>${topic.title.replace(/^\d+\.\s*/, "")}</strong>
      <span>${topic.source}</span>
    </button>
  `).join("");
  document.querySelectorAll(".overview-item").forEach(btn => {
    btn.addEventListener("click", () => {
      activeTopic = btn.dataset.topic;
      completed.add(activeTopic);
      saveProgress();
      renderAll();
    });
  });
}

function renderLesson() {
  const topic = topics.find(item => item.id === activeTopic);
  const mistakesHtml = topic.commonMistakes ? `
    <section>
      <h3>常见误区</h3>
      <ul class="points mistakes">${topic.commonMistakes.map(m => `<li>${m}</li>`).join("")}</ul>
    </section>
  ` : "";

  const toolLinkHtml = topic.toolLink ? `
    <p class="tool-link">关联工具：<button class="link-btn" data-tab="${topic.toolLink}">在右侧打开"${getTabLabel(topic.toolLink)}"工具 →</button></p>
  ` : "";

  document.querySelector("#lessonPanel").innerHTML = `
    <div class="lesson-head">
      <span class="source">${topic.source}</span>
      <h2>${topic.title}</h2>
      <p>${topic.subtitle}</p>
    </div>
    <section class="explain">
      <h3>通俗解释</h3>
      <p>${topic.summary}</p>
      <div class="analogy">${topic.analogy}</div>
    </section>
    <section>
      <h3>课堂要点</h3>
      <ul class="points">${topic.keyPoints.map(point => `<li>${point}</li>`).join("")}</ul>
    </section>
    <section class="case-box">
      <h3>${topic.caseTitle}</h3>
      <p>${topic.caseBody}</p>
    </section>
    ${mistakesHtml}
    ${toolLinkHtml}
    <section class="teacher-tip ${teacherMode ? "show" : ""}">
      <h3>教师提示</h3>
      <p>${topic.teacherTip}</p>
    </section>
  `;

  // 绑定关联工具链接
  document.querySelectorAll(".link-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const tabName = btn.dataset.tab;
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-page").forEach(p => p.classList.remove("active"));
      const tabBtn = document.querySelector(`.tab[data-tab="${tabName}"]`);
      const tabPage = document.querySelector(`#${tabName}Tab`);
      if (tabBtn) tabBtn.classList.add("active");
      if (tabPage) tabPage.classList.add("active");
      // 滚动到工具面板
      document.querySelector(".tool-panel").scrollIntoView({ behavior: "smooth" });
    });
  });
}

function getTabLabel(tabId) {
  const map = { closure: "闭包", keys: "候选键", mincover: "最小覆盖", normform: "范式检查", chase: "Chase" };
  return map[tabId] || tabId;
}

// ==================== 习题渲染 ====================

function renderQuiz() {
  const exercises = exercisesByTopic[activeTopic] || [];
  const sourceLabels = { database: "来自数据库", fallback: "来自本地备用数据", loading: "正在加载" };
  document.querySelector("#quizSource").textContent =
    `${sourceLabels[exerciseSource] || exerciseSource}，当前主题共 ${exercises.length} 题。`;

  const quizTab = document.querySelector("#quizTab");
  // 保留标题和来源文本、学生输入框，只更新列表部分
  const existingList = quizTab.querySelector(".exercise-list");
  if (existingList) {
    existingList.innerHTML = exercises.length
      ? exercises.map(renderExerciseCard).join("")
      : "<div class='result-box'>暂无练习题。如果数据库未连接，将使用本地备用题目。</div>";
    bindExerciseButtons(existingList);
  }
}

function renderExerciseCard(exercise) {
  return `
    <div class="exercise-card" data-exercise="${exercise.id}">
      <div class="exercise-meta">
        ${exercise.question_type === "judge" ? "判断题" : "选择题"}
        · <span class="diff-tag diff-${exercise.difficulty || '基础'}">${exercise.difficulty || "基础"}</span>
      </div>
      <p class="quiz-q">${exercise.question}</p>
      <div class="exercise-options">
        ${(exercise.options || []).map((option, index) =>
          `<button data-exercise="${exercise.id}" data-answer="${index}">${String.fromCharCode(65 + index)}. ${option}</button>`
        ).join("")}
      </div>
      <div id="exerciseResult${exercise.id}" class="result-box hidden"></div>
    </div>
  `;
}

function bindExerciseButtons(listEl) {
  listEl.querySelectorAll(".exercise-options button").forEach(btn => {
    btn.addEventListener("click", () => {
      submitExerciseAnswer(btn);
    });
  });
}

async function submitExerciseAnswer(btn) {
  const exerciseId = Number(btn.dataset.exercise);
  const chosen = btn.dataset.answer;
  const exercise = Object.values(exercisesByTopic).flat().find(item => Number(item.id) === exerciseId);
  if (!exercise) return;

  const studentInput = document.querySelector("#studentName");
  const studentName = studentInput ? studentInput.value.trim() : "匿名学生";
  localStorage.setItem("studentName", studentName || "匿名学生");

  try {
    const response = await fetch("/api/submit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ exercise_id: exerciseId, student_name: studentName || "匿名学生", submitted_answer: chosen }),
    });
    const result = await response.json();
    showExerciseResult(btn, exercise, result);
  } catch {
    const ok = chosen === String(exercise.answer);
    showExerciseResult(btn, exercise, { ok: true, is_correct: ok, correct_answer: exercise.answer, explanation: exercise.explanation, message: "无法连接后端，已在浏览器本地判题。" });
  }
}

function showExerciseResult(btn, exercise, result) {
  const card = btn.closest(".exercise-card");
  card.querySelectorAll(".exercise-options button").forEach(item => item.classList.remove("right", "wrong"));
  btn.classList.add(result.is_correct ? "right" : "wrong");
  const resultBox = document.querySelector(`#exerciseResult${exercise.id}`);
  if (!resultBox) return;
  resultBox.classList.remove("hidden");
  const correctAnswer = result.correct_answer !== undefined ? result.correct_answer : exercise.answer;
  const correctLabel = (exercise.options || [])[Number(correctAnswer)] || correctAnswer;
  resultBox.innerHTML = `
    <strong>${result.is_correct ? "回答正确" : "再想一步"}</strong><br>
    正确答案：${correctLabel}<br>
    ${result.explanation || exercise.explanation || ""}
    ${result.message ? `<br><span class="muted">${result.message}</span>` : ""}
  `;
}

// ==================== 进度 ====================

function renderProgress() {
  const count = completed.size;
  document.querySelector("#progressBar").style.width = `${count / topics.length * 100}%`;
  document.querySelector("#progressText").textContent = `${count} / ${topics.length} 个主题`;
}

function saveProgress() {
  localStorage.setItem("completedTopics", JSON.stringify([...completed]));
}

// ==================== 主渲染 ====================

function renderAll() {
  renderNav();
  renderOverview();
  renderLesson();
  renderQuiz();
  renderProgress();
  document.querySelector("#teacherModeBtn").classList.toggle("active", teacherMode);
}

// ==================== 交互工具 ====================

function renderToolPresets() {
  // 为每个工具的预设按钮绑定事件
  Object.keys(toolPresets).forEach(toolId => {
    const container = document.querySelector(`#${toolId}Presets`);
    if (!container) return;
    const presets = toolPresets[toolId];
    container.innerHTML = `<span class="preset-label">预设示例：</span>` +
      presets.map((p, i) => `<button class="preset-btn" data-tool="${toolId}" data-index="${i}">${p.label}</button>`).join("");

    container.querySelectorAll(".preset-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const tool = btn.dataset.tool;
        const idx = parseInt(btn.dataset.index);
        const preset = toolPresets[tool][idx];
        loadPreset(tool, preset);
      });
    });
  });
}

function loadPreset(tool, preset) {
  if (preset.x !== undefined) document.querySelector("#closureX").value = preset.x;
  if (preset.fds !== undefined) {
    const fdsEl = document.querySelector(`#${tool}Fds`) || document.querySelector("#closureFds");
    if (fdsEl) fdsEl.value = preset.fds;
  }
  if (preset.attrs !== undefined) {
    const attrsEl = document.querySelector(`#${tool}Attrs`) || document.querySelector("#keysAttrs");
    if (attrsEl) attrsEl.value = preset.attrs;
  }
  if (preset.decomp !== undefined) {
    const decompEl = document.querySelector("#chaseDecomp");
    if (decompEl) decompEl.value = preset.decomp;
  }
  // 自动切换到对应 tab
  const tabBtn = document.querySelector(`.tab[data-tab="${tool}"]`);
  if (tabBtn) tabBtn.click();
}

// 通用：解析 FD 文本为数组
function parseFds(text) {
  if (!text.trim()) return [];
  return text.trim().split("\n").map(line => {
    const parts = line.split("→");
    if (parts.length === 2) return [parts[0].trim(), parts[1].trim()];
    return null;
  }).filter(Boolean);
}

// 闭包计算
async function doClosure() {
  const x = document.querySelector("#closureX").value.trim();
  const fdsText = document.querySelector("#closureFds").value.trim();
  const resultBox = document.querySelector("#closureResult");

  if (!x) { resultBox.innerHTML = "<p class='warn-text'>请输入属性集 X。</p>"; return; }
  const fds = parseFds(fdsText);
  if (!fds.length) { resultBox.innerHTML = "<p class='warn-text'>请输入函数依赖集。</p>"; return; }

  resultBox.innerHTML = "<p>计算中...</p>";
  try {
    const resp = await fetch("/api/compute-closure", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ x, fds }),
    });
    const data = await resp.json();
    if (!data.ok) { resultBox.innerHTML = `<p class='warn-text'>错误：${data.message}</p>`; return; }

    let html = `<div class="calc-summary"><strong>X⁺ = ${data.closure_str}</strong>`;
    if (data.is_superkey) html += ` <span class="badge badge-key">是超键</span>`;
    html += `<p class="muted">${data.superkey_note}</p></div>`;

    if (data.steps && data.steps.length) {
      html += "<div class='step-list'><strong>推导过程：</strong><ol>";
      data.steps.forEach(s => {
        html += `<li><code>${s.trigger}</code> → 加入 <strong>${s.added}</strong>，当前闭包 = ${s.closure_after}</li>`;
      });
      html += "</ol></div>";
    } else {
      html += "<p>无更多属性可推出。</p>";
    }
    resultBox.innerHTML = html;
  } catch (e) {
    resultBox.innerHTML = `<p class='warn-text'>请求失败：${e.message}</p>`;
  }
}

// 候选键求解
async function doKeys() {
  const attrsText = document.querySelector("#keysAttrs").value.trim();
  const fdsText = document.querySelector("#keysFds").value.trim();
  const resultBox = document.querySelector("#keysResult");

  const attrs = attrsText.split(/[,，\s]+/).filter(Boolean);
  if (!attrs.length) { resultBox.innerHTML = "<p class='warn-text'>请输入属性集。</p>"; return; }
  const fds = parseFds(fdsText);
  if (!fds.length) { resultBox.innerHTML = "<p class='warn-text'>请输入函数依赖集。</p>"; return; }

  resultBox.innerHTML = "<p>计算中...</p>";
  try {
    const resp = await fetch("/api/find-keys", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ attributes: attrs, fds }),
    });
    const data = await resp.json();
    if (!data.ok) { resultBox.innerHTML = `<p class='warn-text'>错误：${data.message}</p>`; return; }

    let html = `<div class="calc-summary"><strong>候选键：${data.keys_str.map(k => `<span class="badge badge-key">${k}</span>`).join(" ") || "无"}</strong>`;
    html += `<p class="muted">属性集 U = ${data.all_attrs_str}</p></div>`;

    if (data.steps && data.steps.length) {
      html += "<div class='step-list'><strong>检查过程：</strong><ol>";
      data.steps.forEach(s => {
        const cls = s.result === "候选键" ? "step-found" : "";
        html += `<li class="${cls}">检查 <strong>${s.checked}</strong> → 闭包 = ${s.closure}，<span>${s.result}</span>`;
        if (s.note) html += `<br><small class="muted">${s.note}</small>`;
        html += "</li>";
      });
      html += "</ol></div>";
    }
    resultBox.innerHTML = html;
  } catch (e) {
    resultBox.innerHTML = `<p class='warn-text'>请求失败：${e.message}</p>`;
  }
}

// 最小依赖集
async function doMincover() {
  const fdsText = document.querySelector("#mincoverFds").value.trim();
  const resultBox = document.querySelector("#mincoverResult");
  const fds = parseFds(fdsText);
  if (!fds.length) { resultBox.innerHTML = "<p class='warn-text'>请输入函数依赖集。</p>"; return; }

  resultBox.innerHTML = "<p>计算中...</p>";
  try {
    const resp = await fetch("/api/minimal-cover", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fds }),
    });
    const data = await resp.json();
    if (!data.ok) { resultBox.innerHTML = `<p class='warn-text'>错误：${data.message}</p>`; return; }

    let html = `<div class="calc-summary"><strong>最小依赖集：</strong> ${formatFdList(data.minimal_cover)}</div>`;

    ["step1", "step2", "step3"].forEach(stepKey => {
      const step = data[stepKey];
      if (!step) return;
      html += `<div class="step-section"><h4>${step.description}</h4>`;
      if (step.steps && step.steps.length) {
        html += "<ul class='step-items'>";
        step.steps.forEach(s => {
          html += `<li><strong>${s.action}</strong><br><small>${s.detail || ""}</small> → <span class="${s.result.includes('冗余') || s.result.includes('删除') ? 'warn-text' : ''}">${s.result}</span></li>`;
        });
        html += "</ul>";
      }
      html += `<p class="muted">当前结果：${formatFdList(step.result)}</p></div>`;
    });

    resultBox.innerHTML = html;
  } catch (e) {
    resultBox.innerHTML = `<p class='warn-text'>请求失败：${e.message}</p>`;
  }
}

function formatFdList(fds) {
  if (!fds || !fds.length) return "无";
  return fds.map(fd => `<code>${fd[0]}→${fd[1]}</code>`).join("，");
}

// 范式检查
async function doNormform() {
  const attrsText = document.querySelector("#normformAttrs").value.trim();
  const fdsText = document.querySelector("#normformFds").value.trim();
  const resultBox = document.querySelector("#normformResult");

  const attrs = attrsText.split(/[,，\s]+/).filter(Boolean);
  if (!attrs.length) { resultBox.innerHTML = "<p class='warn-text'>请输入属性集。</p>"; return; }
  const fds = parseFds(fdsText);

  resultBox.innerHTML = "<p>计算中...</p>";
  try {
    const resp = await fetch("/api/normal-form", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ attributes: attrs, fds }),
    });
    const data = await resp.json();
    if (!data.ok) { resultBox.innerHTML = `<p class='warn-text'>错误：${data.message}</p>`; return; }

    const nfColors = { "1NF": "#a23838", "2NF": "#a35d18", "3NF": "#1f7a68", "BCNF": "#155f51" };
    let html = `<div class="calc-summary"><strong>最高范式：<span style="color:${nfColors[data.highest_nf] || '#333'};font-size:1.3em;">${data.highest_nf}</span></strong>`;
    html += `<p class="muted">候选键：${(data.candidate_keys || []).map(k => k.join("")).join("，") || "无"}</p>`;
    html += `<p class="muted">主属性：{${(data.prime_attrs || []).join(", ")}} | 非主属性：{${(data.non_prime_attrs || []).join(", ")}}</p></div>`;

    html += "<div class='nf-checklist'>";
    ["1NF", "2NF", "3NF", "BCNF"].forEach(nf => {
      const satisfied = data[`is_${nf.toLowerCase().replace("1nf","1nf")}`];
      // Fix key mapping
      const keyMap = { "1NF": "is_1nf", "2NF": "is_2nf", "3NF": "is_3nf", "BCNF": "is_bcnf" };
      const ok = data[keyMap[nf]];
      html += `<div class="nf-item ${ok ? "nf-ok" : "nf-fail"}">${nf}: ${ok ? "✓ 满足" : "✗ 不满足"}</div>`;
    });
    html += "</div>";

    if (data.violations && data.violations.length) {
      html += "<div class='step-list'><strong>违规依赖：</strong><ul>";
      data.violations.forEach(v => {
        html += `<li><code>${v.fd}</code> — 违反 ${v.nf}：${v.reason}</li>`;
      });
      html += "</ul></div>";
    }

    html += `<p class="muted" style="white-space:pre-line;">${data.analysis}</p>`;
    resultBox.innerHTML = html;
  } catch (e) {
    resultBox.innerHTML = `<p class='warn-text'>请求失败：${e.message}</p>`;
  }
}

// Chase 过程
async function doChase() {
  const attrsText = document.querySelector("#chaseAttrs").value.trim();
  const fdsText = document.querySelector("#chaseFds").value.trim();
  const decompText = document.querySelector("#chaseDecomp").value.trim();
  const resultBox = document.querySelector("#chaseResult");

  const attrs = attrsText.split(/[,，\s]+/).filter(Boolean);
  const decomp = decompText.split("\n").map(line => line.trim().split(/[,，\s]*/).filter(Boolean)).filter(a => a.length);
  const fds = parseFds(fdsText);

  if (!attrs.length || !decomp.length) { resultBox.innerHTML = "<p class='warn-text'>请填写完整信息。</p>"; return; }

  resultBox.innerHTML = "<p>计算中...</p>";
  try {
    const resp = await fetch("/api/chase-test", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ attributes: attrs, fds, decomposition: decomp }),
    });
    const data = await resp.json();
    if (!data.ok) { resultBox.innerHTML = `<p class='warn-text'>错误：${data.message}</p>`; return; }

    let html = "";
    // 初始表格
    html += "<div class='step-section'><h4>初始表格</h4>";
    html += renderChaseTable(data.all_attrs, data.initial_table);
    html += "</div>";

    // Chase 步骤
    if (data.steps && data.steps.length) {
      html += "<div class='step-section'><h4>Chase 过程</h4>";
      data.steps.forEach((s, i) => {
        html += `<div class="chase-step"><p><strong>步骤 ${i + 1}：</strong>应用 <code>${s.fd}</code> — ${s.note}</p>`;
        html += renderChaseTable(data.all_attrs, s.table_snapshot);
        html += "</div>";
      });
      html += "</div>";
    }

    // 最终表格与判定
    html += "<div class='step-section'><h4>最终表格</h4>";
    html += renderChaseTable(data.all_attrs, data.final_table);
    html += "</div>";

    html += `<div class="calc-summary"><strong>判定结果：</strong>`;
    if (data.is_lossless) {
      html += `<span class="badge badge-key">无损分解</span>（第 ${data.all_a_row_index + 1} 行为全 a 行）`;
    } else {
      html += `<span class="badge badge-warn">有损分解</span>（不存在全 a 行）`;
    }
    html += "</div>";

    resultBox.innerHTML = html;
  } catch (e) {
    resultBox.innerHTML = `<p class='warn-text'>请求失败：${e.message}</p>`;
  }
}

function renderChaseTable(attrs, table) {
  let html = "<table class='chase-table'><tr><th></th>";
  attrs.forEach(a => { html += `<th>${a}</th>`; });
  html += "</tr>";
  table.forEach((row, i) => {
    const isAllA = row.every(cell => cell.startsWith("a"));
    html += `<tr class="${isAllA ? "all-a-row" : ""}"><td><strong>R${i + 1}</strong></td>`;
    row.forEach(cell => {
      const cls = cell.startsWith("a") ? "cell-a" : "cell-b";
      html += `<td class="${cls}">${cell}</td>`;
    });
    html += "</tr>";
  });
  html += "</table>";
  return html;
}

// ==================== 案例库 ====================

let allCases = [];

async function loadCases() {
  try {
    const resp = await fetch("/api/cases");
    const data = await resp.json();
    if (data.ok) allCases = data.data;
  } catch {
    allCases = [];
  }
}

function openCaseLibrary() {
  document.querySelector("#caseModal").classList.remove("hidden");
  document.querySelector("#caseDetail").classList.add("hidden");
  document.querySelector("#caseGrid").classList.remove("hidden");
  renderCaseGrid();
}

function closeCaseLibrary() {
  document.querySelector("#caseModal").classList.add("hidden");
}

function renderCaseGrid() {
  const grid = document.querySelector("#caseGrid");
  if (!allCases.length) {
    grid.innerHTML = "<p>案例库加载失败，请检查后端是否正常运行。</p>";
    return;
  }
  grid.innerHTML = allCases.map(c => `
    <button class="case-card" data-case="${c.id}">
      <span class="case-card-tags">${(c.tags || []).map(t => `<span class="tag">${t}</span>`).join(" ")}</span>
      <strong>${c.title}</strong>
      <small>${c.section}</small>
      <p>${c.scenario.substring(0, 60)}...</p>
    </button>
  `).join("");

  grid.querySelectorAll(".case-card").forEach(btn => {
    btn.addEventListener("click", () => {
      const caseId = btn.dataset.case;
      showCaseDetail(caseId);
    });
  });
}

function showCaseDetail(caseId) {
  const c = allCases.find(item => item.id === caseId);
  if (!c) return;
  currentCaseId = caseId;
  document.querySelector("#caseGrid").classList.add("hidden");
  const detail = document.querySelector("#caseDetail");
  detail.classList.remove("hidden");

  const problemsHtml = (c.problems || []).map(p => `
    <div class="problem-card">
      <strong class="warn-text">${p.type}</strong>
      <p>${p.detail}</p>
    </div>
  `).join("");

  const decompHtml = c.solution ? `
    <div class="step-section">
      <h4>分解方案：${c.solution.method}</h4>
      <div class="decomp-list">
        ${(c.solution.decomposition || []).map(d => `
          <div class="decomp-item">
            <strong>${d.name}</strong>
            <span>属性：{${(d.attrs || []).join(", ")}}</span>
            <span>主键：{${(d.key || []).join(", ")}}</span>
            ${d.note ? `<small>${d.note}</small>` : ""}
          </div>
        `).join("")}
      </div>
      ${c.solution.lossless !== undefined ? `<p>无损连接：${c.solution.lossless ? "✓ 是" : "✗ 否"} | 保持依赖：${c.solution.dependency_preserving !== undefined ? (c.solution.dependency_preserving ? "✓ 是" : "✗ 否") : "—"}</p>` : ""}
      ${c.solution.note ? `<p class="muted">${c.solution.note}</p>` : ""}
    </div>
  ` : "";

  const mvdsHtml = c.mvds ? `
    <div><strong>多值依赖：</strong>${c.mvds.map(m => `<code>${m[0]}→→${m[1]}</code>`).join("，")}</div>
  ` : "";

  const loadToolHtml = c.attributes && c.fds ? `
    <button class="primary" id="loadCaseToTool" style="margin-top:12px;">加载此案例到范式检查器</button>
  ` : "";

  document.querySelector("#caseDetailContent").innerHTML = `
    <h2>${c.title}</h2>
    <p class="muted">${c.section} | ${(c.tags || []).join(" · ")}</p>
    <section class="case-box"><p>${c.scenario}</p></section>
    <div class="step-section">
      <h4>基本信息</h4>
      <p><strong>关系模式：</strong>${c.relation || ""}</p>
      <p><strong>函数依赖集：</strong>${(c.fds || []).map(fd => `<code>${fd[0]}→${fd[1]}</code>`).join("，") || "无"}</p>
      ${mvdsHtml}
      <p><strong>候选键：</strong>${(c.candidate_keys || []).map(k => k.join("")).join("，") || "—"}</p>
      <p><strong>最高范式：</strong><span class="badge">${c.highest_nf || "—"}</span></p>
    </div>
    ${problemsHtml ? `<div class="step-section"><h4>存在的问题</h4>${problemsHtml}</div>` : ""}
    ${decompHtml}
    <div class="step-section">
      <h4>关键知识点</h4>
      <ul class="points">${(c.key_points || []).map(p => `<li>${p}</li>`).join("")}</ul>
    </div>
    ${c.teaching_tip ? `<section class="teacher-tip show"><h4>教学提示</h4><p>${c.teaching_tip}</p></section>` : ""}
    ${loadToolHtml}
  `;

  // 绑定加载到工具按钮
  const loadBtn = document.querySelector("#loadCaseToTool");
  if (loadBtn) {
    loadBtn.addEventListener("click", () => {
      const fdsText = (c.fds || []).map(fd => `${fd[0]}→${fd[1]}`).join("\n");
      document.querySelector("#normformAttrs").value = (c.attributes || []).join(",");
      document.querySelector("#normformFds").value = fdsText;
      closeCaseLibrary();
      document.querySelector(".tab[data-tab='normform']").click();
      document.querySelector(".tool-panel").scrollIntoView({ behavior: "smooth" });
    });
  }
}

// ==================== 事件绑定 ====================

document.addEventListener("DOMContentLoaded", () => {
  // Tab 切换
  document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-page").forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const target = document.querySelector(`#${tab.dataset.tab}Tab`);
      if (target) target.classList.add("active");
    });
  });

  // 工具按钮
  document.querySelector("#closureBtn").addEventListener("click", doClosure);
  document.querySelector("#keysBtn").addEventListener("click", doKeys);
  document.querySelector("#mincoverBtn").addEventListener("click", doMincover);
  document.querySelector("#normformBtn").addEventListener("click", doNormform);
  document.querySelector("#chaseBtn").addEventListener("click", doChase);

  // 工具预设
  renderToolPresets();

  // 教师模式
  document.querySelector("#teacherModeBtn").addEventListener("click", () => {
    teacherMode = !teacherMode;
    localStorage.setItem("teacherMode", teacherMode ? "1" : "0");
    renderAll();
  });

  // 重置
  document.querySelector("#resetBtn").addEventListener("click", () => {
    completed = new Set();
    saveProgress();
    renderAll();
  });

  // 学生姓名
  document.querySelector("#studentName").addEventListener("input", e => {
    localStorage.setItem("studentName", e.target.value);
  });

  // 案例库
  document.querySelector("#caseLibBtn").addEventListener("click", openCaseLibrary);
  document.querySelector("#closeCaseModal").addEventListener("click", closeCaseLibrary);
  document.querySelector("#caseModal .modal-overlay").addEventListener("click", closeCaseLibrary);
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeCaseLibrary();
  });
  document.querySelector("#backToCaseList").addEventListener("click", () => {
    document.querySelector("#caseDetail").classList.add("hidden");
    document.querySelector("#caseGrid").classList.remove("hidden");
  });

  // 初始化
  completed.add(activeTopic);
  saveProgress();
  loadCases();
  loadDatabaseStatus();
  loadExercises();
  renderAll();
});

// ==================== 数据加载 ====================

async function loadDatabaseStatus() {
  const status = document.querySelector("#dbStatus");
  try {
    const resp = await fetch("/api/db-status");
    const data = await resp.json();
    if (data.ok) {
      status.textContent = `数据库已连接：${data.database}`;
      status.classList.add("ok");
    } else {
      status.textContent = `数据库未连接：${data.message}（使用本地备用数据）`;
      status.classList.add("warn");
    }
  } catch {
    status.textContent = "后端服务不可用，使用本地备用数据。";
    status.classList.add("warn");
  }
}

async function loadExercises() {
  try {
    const resp = await fetch("/api/exercises");
    const data = await resp.json();
    exerciseSource = data.source || "database";
    exercisesByTopic = data.data.reduce((grouped, ex) => {
      (grouped[ex.topic_key] = grouped[ex.topic_key] || []).push(ex);
      return grouped;
    }, {});
  } catch {
    exerciseSource = "fallback";
    // 使用 seed_data 中内置的题目
    exercisesByTopic = {};
  }
  renderQuiz();
}

// 恢复上次学生姓名
document.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("studentName");
  if (saved) {
    const input = document.querySelector("#studentName");
    if (input) input.value = saved;
  }
});
