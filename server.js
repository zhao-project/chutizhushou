/**
 * 出题助手 - 轻量 Web 服务器
 * 提供前端页面 + 模拟 API（Python 后端就绪后可切换）
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;

// 模拟题目数据（用于前端演示）
const MOCK_QUESTIONS = [
  {
    question_type: "choice",
    difficulty: "easy",
    content: "下列方程中，是一元一次方程的是（ ）",
    options: ["A. x² + 2x = 1", "B. 3x - 5 = 0", "C. x + y = 3", "D. 2/x = 4"],
    answer: "B",
    explanation: "一元一次方程要求：只有一个未知数、次数为1、整式方程",
    knowledge_point: "一元一次方程定义"
  },
  {
    question_type: "choice",
    difficulty: "medium",
    content: "方程 2x - 6 = 0 的解是（ ）",
    options: ["A. x = 1", "B. x = 2", "C. x = 3", "D. x = 4"],
    answer: "C",
    explanation: "移项得 2x = 6，系数化1得 x = 3",
    knowledge_point: "解一元一次方程"
  },
  {
    question_type: "fill",
    difficulty: "easy",
    content: "方程 3x + 9 = 0 的解为 x = ____。",
    answer: "-3",
    knowledge_point: "解一元一次方程"
  },
  {
    question_type: "fill",
    difficulty: "medium",
    content: "若关于x的方程 (a-2)x + 3 = 0 是一元一次方程，则 a 的取值范围是 ____。",
    answer: "a ≠ 2",
    explanation: "系数a-2不能为0",
    knowledge_point: "一元一次方程定义"
  },
  {
    question_type: "true_false",
    difficulty: "easy",
    content: "方程 5x = 0 的解是 x = 0。",
    answer: "✓ 正确",
    knowledge_point: "解一元一次方程"
  },
  {
    question_type: "short",
    difficulty: "hard",
    content: "解方程：3(x - 2) + 2 = 2x + 1，并写出完整的解题步骤。",
    answer: "x = 5\n步骤：\n1. 去括号：3x - 6 + 2 = 2x + 1\n2. 整理：3x - 4 = 2x + 1\n3. 移项：3x - 2x = 1 + 4\n4. 合并：x = 5",
    explanation: "注意去括号和移项都要变号",
    knowledge_point: "解一元一次方程步骤"
  },
  {
    question_type: "essay",
    difficulty: "hard",
    content: "小明去超市买文具，买了3支钢笔和5本笔记本，共花了47元。已知每支钢笔比每本笔记本贵3元。求钢笔和笔记本的单价各是多少元？",
    answer: "设笔记本单价为x元，则钢笔为(x+3)元\n3(x+3) + 5x = 47 → x = 4.75\n笔记本4.75元，钢笔7.75元",
    knowledge_point: "一元一次方程应用题"
  }
];

// 路由
const routes = {
  'GET /': (req, res) => {
    serveFile(res, path.join(__dirname, 'web', 'index.html'), 'text/html');
  },
  'GET /api/generate': (req, res) => {
    let body = '';
    req.on('data', chunk => body += chunk);
    req.on('end', () => {
      try {
        const data = JSON.parse(body);
        const count = data.question_count || MOCK_QUESTIONS.length;
        const questions = MOCK_QUESTIONS.slice(0, count);
        const title = `${data.subject}${data.grade ? ' - ' + data.grade : ''}${data.chapter ? ' - ' + data.chapter : ''} 练习题`;
        res.writeHead(200, { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' });
        res.end(JSON.stringify({
          title,
          subject: data.subject,
          grade: data.grade || null,
          chapter: data.chapter || null,
          total_score: 100,
          duration_min: 90,
          questions
        }));
      } catch (e) {
        res.writeHead(400);
        res.end(JSON.stringify({ error: e.message }));
      }
    });
  },
  'POST /api/generate': (req, res) => {
    routes['GET /api/generate'](req, res);
  },
  'OPTIONS /api/generate': (req, res) => {
    res.writeHead(200, {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    });
    res.end();
  }
};

const server = http.createServer((req, res) => {
  const key = `${req.method} ${req.url.split('?')[0]}`;
  const handler = routes[key];
  if (handler) {
    handler(req, res);
  } else {
    // Try to serve static files
    let filePath = path.join(__dirname, req.url.split('?')[0]);
    if (!path.extname(filePath)) filePath = path.join(__dirname, 'web', 'index.html');
    const ext = path.extname(filePath).toLowerCase();
    const mimeTypes = {
      '.html': 'text/html', '.js': 'application/javascript',
      '.css': 'text/css', '.json': 'application/json',
      '.png': 'image/png', '.jpg': 'image/jpeg', '.gif': 'image/gif'
    };
    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('404 Not Found');
      } else {
        res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain', 'Access-Control-Allow-Origin': '*' });
        res.end(data);
      }
    });
  }
});

function serveFile(res, filePath, contentType) {
  fs.readFile(filePath, (err, data) => {
    if (err) {
      res.writeHead(404);
      res.end('File not found');
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    }
  });
}

server.listen(PORT, () => {
  console.log(`📝 出题助手 Web 界面已启动: http://localhost:${PORT}`);
});
