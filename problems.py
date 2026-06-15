"""Problem bank for Chinese high school / Gaokao-oriented mathematics."""

KNOWLEDGE_POINTS = {
    "sets_logic": "集合与常用逻辑用语",
    "inequalities": "不等式",
    "functions": "函数概念与性质",
    "exponential_log": "指数函数与对数函数",
    "trigonometry": "三角函数",
    "plane_vectors": "平面向量",
    "complex_numbers": "复数",
    "sequences": "数列",
    "derivatives": "导数及其应用",
    "solid_geometry": "立体几何",
    "space_vectors": "空间向量与立体几何",
    "analytic_geometry": "直线与圆",
    "conic_sections": "圆锥曲线",
    "counting_binomial": "计数原理与二项式定理",
    "probability": "概率与随机变量",
    "statistics": "统计与回归分析",
    "modeling": "数学建模与综合应用",
}

SAMPLE_PROBLEMS = [
    {"problem_id":"SET001","question":"已知集合 A={x|x^2-3x+2=0}, B={1,2,3}，求 A∩B。","correct_answer":"{1,2}","knowledge_point":"sets_logic","difficulty":1,"solution":"由 x^2-3x+2=(x-1)(x-2)=0，得 A={1,2}。因此 A∩B={1,2}。"},
    {"problem_id":"INEQ001","question":"解不等式 x^2-5x+6>0，并用区间表示。","correct_answer":"(-oo,2)U(3,oo)","knowledge_point":"inequalities","difficulty":2,"solution":"x^2-5x+6=(x-2)(x-3)。开口向上，大于0在两根外侧，所以解集为 (-∞,2)∪(3,∞)。"},
    {"problem_id":"FUNC001","question":"已知函数 f(x)=x^2-2ax+3 在区间 [1,3] 上单调递增，求实数 a 的取值范围。","correct_answer":"a<=1","knowledge_point":"functions","difficulty":3,"solution":"二次函数开口向上，对称轴为 x=a。要在 [1,3] 上单调递增，需要对称轴在区间左端点左侧或重合，即 a≤1。"},
    {"problem_id":"LOG001","question":"若 log_2(x-1)+log_2(x+1)=3，求 x 的值。","correct_answer":"3","knowledge_point":"exponential_log","difficulty":3,"solution":"定义域要求 x>1。由对数运算得 log_2((x-1)(x+1))=3，所以 x^2-1=8，x^2=9。结合 x>1，得 x=3。"},
    {"problem_id":"TRIG001","question":"已知 sin α=3/5，且 α 为第一象限角，求 cos α。","correct_answer":"4/5","knowledge_point":"trigonometry","difficulty":2,"solution":"由 sin^2α+cos^2α=1，得 cos^2α=1-9/25=16/25。α在第一象限，cosα>0，所以 cosα=4/5。"},
    {"problem_id":"VEC001","question":"已知向量 a=(1,2), b=(3,-1)，求 a·b。","correct_answer":"1","knowledge_point":"plane_vectors","difficulty":1,"solution":"平面向量数量积为对应坐标乘积之和：a·b=1×3+2×(-1)=1。"},
    {"problem_id":"VEC002","question":"已知向量 a=(2,m), b=(3,-1)，若 a⊥b，求 m。","correct_answer":"6","knowledge_point":"plane_vectors","difficulty":2,"solution":"向量垂直时数量积为0，所以 2×3+m×(-1)=0，6-m=0，m=6。"},
    {"problem_id":"CPLX001","question":"计算 (1+i)^2，并写成 a+bi 的形式。","correct_answer":"2i","knowledge_point":"complex_numbers","difficulty":1,"solution":"(1+i)^2=1+2i+i^2=1+2i-1=2i。"},
    {"problem_id":"SEQ001","question":"等差数列 {a_n} 中，a_1=2, a_5=14，求公差 d。","correct_answer":"3","knowledge_point":"sequences","difficulty":2,"solution":"等差数列 a_5=a_1+4d，因此 14=2+4d，d=3。"},
    {"problem_id":"DER001","question":"已知 f(x)=x^3-3x，求 f'(x)。","correct_answer":"3*x^2-3","knowledge_point":"derivatives","difficulty":2,"solution":"按幂函数求导法则，(x^3)'=3x^2，(-3x)'=-3，所以 f'(x)=3x^2-3。"},
    {"problem_id":"SOLID001","question":"一个圆锥的底面半径为3，高为4，求体积。","correct_answer":"12*pi","knowledge_point":"solid_geometry","difficulty":2,"solution":"圆锥体积 V=1/3·πr^2h=1/3×π×9×4=12π。"},
    {"problem_id":"SPACEV001","question":"已知空间向量 a=(1,2,2), b=(2,-1,0)，求 a·b。","correct_answer":"0","knowledge_point":"space_vectors","difficulty":1,"solution":"空间向量数量积为对应坐标乘积之和：1×2+2×(-1)+2×0=0。"},
    {"problem_id":"LINE001","question":"求过点 (1,2) 且斜率为3的直线方程。","correct_answer":"y=3*x-1","knowledge_point":"analytic_geometry","difficulty":2,"solution":"点斜式为 y-2=3(x-1)，整理得 y=3x-1。"},
    {"problem_id":"CONIC001","question":"椭圆 x^2/9 + y^2/4 = 1 的长半轴长为多少？","correct_answer":"3","knowledge_point":"conic_sections","difficulty":1,"solution":"标准椭圆方程中较大的分母为9，所以长半轴 a=√9=3。"},
    {"problem_id":"COUNT001","question":"从5名学生中选出2名参加活动，有多少种选法？","correct_answer":"10","knowledge_point":"counting_binomial","difficulty":1,"solution":"不考虑顺序，选法数为 C(5,2)=5×4/2=10。"},
    {"problem_id":"PROB001","question":"抛掷一枚均匀硬币3次，恰好出现2次正面的概率是多少？","correct_answer":"3/8","knowledge_point":"probability","difficulty":2,"solution":"总结果数为2^3=8。恰好2次正面的情况数为 C(3,2)=3，所以概率为3/8。"},
    {"problem_id":"STAT001","question":"一组数据 2,4,6,8,10 的平均数是多少？","correct_answer":"6","knowledge_point":"statistics","difficulty":1,"solution":"平均数=(2+4+6+8+10)/5=30/5=6。"},
    {"problem_id":"MODEL001","question":"某商品原价100元，连续两次按相同折扣降价后为81元，求每次折扣率。","correct_answer":"10%","knowledge_point":"modeling","difficulty":3,"solution":"设每次降价率为 r，则 100(1-r)^2=81，(1-r)^2=0.81。取正数，1-r=0.9，所以 r=0.1=10%。"},
]


def get_problem(problem_id):
    for p in SAMPLE_PROBLEMS:
        if p["problem_id"] == problem_id:
            return p
    return None


def get_problems_by_kp(kp):
    return [p for p in SAMPLE_PROBLEMS if p["knowledge_point"] == kp]
