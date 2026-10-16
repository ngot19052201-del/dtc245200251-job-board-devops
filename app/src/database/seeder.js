const fs = require('fs');
const path = require('path');
const bcrypt = require('bcryptjs');
const mysql = require('mysql2/promise');
require('dotenv').config({ path: path.join(__dirname, '../../.env') });

async function runSeed() {
  console.log('[Seeder] Starting database initialization and seeding...');

  const host = process.env.DB_HOST || 'mysql';
  const port = parseInt(process.env.DB_PORT || '3306', 10);
  const user = process.env.DB_USER || 'jobuser';
  const password = process.env.DB_PASSWORD || 'JobPass@2026_Secure';
  const database = process.env.DB_NAME || 'jobboard_db';

  let connection;
  let retries = 15;
  while (retries > 0) {
    try {
      connection = await mysql.createConnection({ host, port, user, password, database, multipleStatements: true });
      console.log('[Seeder] Connected to MySQL database successfully.');
      break;
    } catch (err) {
      retries -= 1;
      console.log(`[Seeder] Waiting for MySQL... (${retries} retries left): ${err.message}`);
      await new Promise(res => setTimeout(res, 3000));
    }
  }

  if (!connection) {
    console.error('[Seeder] Could not connect to MySQL database.');
    process.exit(1);
  }

  try {
    // 1. Run schema init.sql
    const initSqlPath = path.join(__dirname, 'init.sql');
    if (fs.existsSync(initSqlPath)) {
      const initSql = fs.readFileSync(initSqlPath, 'utf8');
      await connection.query(initSql);
      console.log('[Seeder] Schema init.sql executed.');
    }

    // 2. Check if users already seeded
    const [existingUsers] = await connection.query('SELECT COUNT(*) as count FROM users');
    if (existingUsers[0].count > 0) {
      console.log('[Seeder] Database already contains data. Skipping duplicate seed.');
      await connection.end();
      return;
    }

    console.log('[Seeder] Seeding initial data...');

    // 3. Categories
    const categories = [
      ['Công nghệ Thông tin / Phần mềm', 'cntt-phan-mem', 'bi-code-slash', 'Lập trình viên Web, Mobile, Backend, Frontend'],
      ['DevOps & Cloud Systems', 'devops-cloud', 'bi-cloud-check', 'Kỹ sư CI/CD, Quản trị Cloud AWS/GCP, Docker & K8s'],
      ['An toàn Thông tin / Cyber Security', 'cyber-security', 'bi-shield-check', 'Bảo mật hệ thống, Pentest, SOC Analyst, DevSecOps'],
      ['Trí tuệ Nhân tạo & Data Science', 'ai-data-science', 'bi-cpu', 'Kỹ sư Machine Learning, Deep Learning, Big Data'],
      ['Thiết kế UI/UX & Đồ họa', 'ui-ux-design', 'bi-palette', 'Thiết kế giao diện website, ứng dụng di động, đồ họa'],
      ['Quản lý Dự án & Scrum Master', 'project-management', 'bi-kanban', 'Project Manager, Scrum Master, Product Owner']
    ];

    for (const cat of categories) {
      await connection.query(
        'INSERT INTO job_categories (name, slug, icon, description) VALUES (?, ?, ?, ?)',
        cat
      );
    }

    // 4. Users (Admin, Recruiters, Candidates)
    const salt = await bcrypt.genSalt(10);
    const adminPass = await bcrypt.hash('Admin@2026', salt);
    const recruiterPass = await bcrypt.hash('Recruiter@2026', salt);
    const candidatePass = await bcrypt.hash('Candidate@2026', salt);

    // Admin
    const [adminRes] = await connection.query(
      `INSERT INTO users (role, full_name, email, password, phone, status) VALUES 
      ('admin', 'Quản trị viên Hệ thống', 'admin@jobboard.vn', ?, '0988000111', 'active')`,
      [adminPass]
    );

    // Recruiter 1: FPT Software
    const [recruiter1Res] = await connection.query(
      `INSERT INTO users (role, full_name, email, password, phone, status) VALUES 
      ('recruiter', 'Trần Mạnh Dũng - HR Manager', 'recruiter@fpt.vn', ?, '0912345678', 'active')`,
      [recruiterPass]
    );

    // Recruiter 2: Viettel Solutions
    const [recruiter2Res] = await connection.query(
      `INSERT INTO users (role, full_name, email, password, phone, status) VALUES 
      ('recruiter', 'Nguyễn Thu Trang - Tech Recruiter', 'recruiter@viettel.vn', ?, '0977889900', 'active')`,
      [recruiterPass]
    );

    // Candidate 1: Trương Thị Bích Ngọc (Sinh viên đề tài)
    const [cand1Res] = await connection.query(
      `INSERT INTO users (role, full_name, email, password, phone, status) VALUES 
      ('candidate', 'Trương Thị Bích Ngọc', 'bichngoc@jobboard.vn', ?, '0966245251', 'active')`,
      [candidatePass]
    );

    // Candidate 2: Hoàng Văn Nam
    const [cand2Res] = await connection.query(
      `INSERT INTO users (role, full_name, email, password, phone, status) VALUES 
      ('candidate', 'Hoàng Văn Nam', 'namhoang@gmail.com', ?, '0933555777', 'active')`,
      [candidatePass]
    );

    // 5. Companies
    const [fptComp] = await connection.query(
      `INSERT INTO companies (user_id, name, logo, website, address, description, scale) VALUES
      (?, 'FPT Software', '/img/fpt-logo.png', 'https://fptsoftware.com', 'Khu Công nghệ cao Hòa Lạc, Hà Nội', 'Tập đoàn phần mềm hàng đầu Việt Nam cung cấp dịch vụ CNTT toàn cầu.', '10,000+ nhân viên')`,
      [recruiter1Res.insertId]
    );

    const [viettelComp] = await connection.query(
      `INSERT INTO companies (user_id, name, logo, website, address, description, scale) VALUES
      (?, 'Viettel Telecom & Solutions', '/img/viettel-logo.png', 'https://viettel.vn', 'Tòa nhà Viettel, Cầu Giấy, Hà Nội', 'Tập đoàn Công nghiệp - Viễn thông Quân đội tiên phong chuyển đổi số.', '5,000+ nhân viên')`,
      [recruiter2Res.insertId]
    );

    // 6. Candidate Profiles
    await connection.query(
      `INSERT INTO candidate_profiles (user_id, title, bio, skills, experience, education, cv_file) VALUES
      (?, 'DevOps & Full-stack Engineer', 'Sinh viên ngành Công nghệ Thông tin trường ĐH CNTT&TT Thái Nguyên (ICTU), đam mê nghiên cứu kiến trúc microservices, containerization Docker, CI/CD và giám sát hệ thống.', 'Node.js, Docker, Nginx, Prometheus, Grafana, Linux, MySQL, Git', '1 năm kinh nghiệm thực tập & đồ án', 'Đại học CNTT và Truyền thông - ĐH Thái Nguyên (Khóa K23)', '/uploads/cvs/CV_TruongThiBichNgoc_DTC245200251.pdf')`,
      [cand1Res.insertId]
    );

    await connection.query(
      `INSERT INTO candidate_profiles (user_id, title, bio, skills, experience, education, cv_file) VALUES
      (?, 'Junior Backend Developer', 'Lập trình viên backend Node.js & Python tìm kiếm cơ hội thử sức trong môi trường chuyên nghiệp.', 'Node.js, Express, MySQL, REST API, Git', '6 tháng kinh nghiệm', 'Đại học Thái Nguyên', NULL)`,
      [cand2Res.insertId]
    );

    // 7. Jobs
    const jobs = [
      [
        fptComp.insertId,
        2, // DevOps
        'Senior DevOps Engineer (Docker, K8s, CI/CD)',
        'Xây dựng và tối ưu hệ thống CI/CD pipeline, quản lý hạ tầng container Kubernetes và triển khai hệ thống giám sát Prometheus, Grafana, Loki cho khách hàng quốc tế.',
        '- Tối thiểu 2 năm kinh nghiệm quản trị Linux, Docker và CI/CD.\n- Nắm vững kiến thức mạng máy tính, Nginx reverse proxy, SSL/TLS.\n- Có kinh nghiệm với hệ thống monitoring (Prometheus, Grafana, Loki).\n- Tiếng Anh giao tiếp tốt.',
        '- Lương hấp dẫn 25 - 40 triệu VNĐ/tháng, thưởng dự án theo quý.\n- Bảo hiểm FPT Care cho bản thân và gia đình.\n- Cơ hội onsite làm việc tại Nhật Bản, Mỹ, châu Âu.',
        '25,000,000 - 40,000,000 VNĐ',
        'Hà Nội (Hỗ trợ xe đưa đón)',
        'Toàn thời gian',
        'approved',
        '2026-12-31'
      ],
      [
        fptComp.insertId,
        1, // IT / Phần mềm
        'Full-stack Web Developer (Node.js / Vue.js)',
        'Tham gia phát triển các nền tảng web ứng dụng lớn, xử lý hàng triệu người dùng cho các thị trường Fintech và E-commerce.',
        '- Có kinh nghiệm với Node.js (Express), JavaScript ES6+, HTML5, CSS3.\n- Sử dụng thành thạo cơ sở dữ liệu quan hệ MySQL và NoSQL.\n- Kỹ năng làm việc nhóm và giải quyết vấn đề tốt.',
        '- Lương từ 18 - 30 triệu VNĐ tùy năng lực.\n- Môi trường trẻ trung, cơ hội thăng tiến rõ ràng.\n- Đào tạo chứng chỉ quốc tế miễn phí.',
        '18,000,000 - 30,000,000 VNĐ',
        'Hà Nội / Thái Nguyên (Hybrid)',
        'Toàn thời gian',
        'approved',
        '2026-11-30'
      ],
      [
        viettelComp.insertId,
        3, // Cyber Security
        'Chuyên viên An toàn Thông tin & DevSecOps',
        'Đảm bảo an ninh an toàn thông tin cho hạ tầng viễn thông số, phân tích lỗ hổng bảo mật, thiết lập chính sách Nginx Security Headers, Firewall và giám sát log tập trung.',
        '- Tốt nghiệp đại học chuyên ngành CNTT, An toàn thông tin.\n- Hiểu sâu về OWASP Top 10, cấu hình hardening máy chủ Linux, container security.\n- Có các chứng chỉ CEH, Security+, OSCP là lợi thế lớn.',
        '- Thu nhập 22 - 35 triệu/tháng, thưởng các ngày lễ tết theo quy định Tập đoàn.\n- Tiếp cận các công nghệ an ninh mạng hàng đầu thế giới.',
        '22,000,000 - 35,000,000 VNĐ',
        'Hà Nội',
        'Toàn thời gian',
        'approved',
        '2026-12-15'
      ],
      [
        viettelComp.insertId,
        2, // DevOps
        'Quản trị Hệ thống Linux & Cloud Infrastructure (Junior/Mid)',
        'Vận hành máy chủ Linux, triển khai giải pháp container hóa, cấu hình Nginx Reverse Proxy, MySQL Cluster và hệ thống cảnh báo tự động.',
        '- Thành thạo lệnh dòng lệnh Linux (Ubuntu, RHEL).\n- Hiểu về Docker Compose, Bash script tự động hóa.\n- Nhiệt tình, có trách nhiệm và mong muốn phát triển dài hạn.',
        '- Thu nhập khởi điểm 15 - 22 triệu VNĐ.\n- Được cấp laptop cấu hình cao, phụ cấp ăn trưa và gửi xe.',
        '15,000,000 - 22,000,000 VNĐ',
        'Thái Nguyên / Hà Nội',
        'Toàn thời gian',
        'approved',
        '2026-12-30'
      ],
      [
        fptComp.insertId,
        4, // AI
        'Kỹ sư Trí tuệ Nhân tạo & Xử lý Dữ liệu lớn (AI Engineer)',
        'Nghiên cứu và triển khai mô hình học máy (Machine Learning/Deep Learning) cho các bài toán xử lý ngôn ngữ tự nhiên và phân tích dữ liệu tuyển dụng thông minh.',
        '- Nắm vững Python, PyTorch/TensorFlow, SQL.\n- Có tư duy toán học và giải thuật tốt.',
        '- Thu nhập cạnh tranh 20 - 35 triệu/tháng.\n- Thưởng hiệu quả nghiên cứu và công bố bài báo khoa học.',
        '20,000,000 - 35,000,000 VNĐ',
        'Hà Nội / Remote',
        'Remote',
        'approved',
        '2026-12-31'
      ],
      [
        viettelComp.insertId,
        1, // IT
        'Thực tập sinh Quản trị Hệ thống & DevOps (Internship)',
        'Chương trình đào tạo thực tế dành cho sinh viên năm 3, năm cuối: Làm quen với Docker, CI/CD, Nginx, Prometheus, Linux System Administration.',
        '- Sinh viên chuyên ngành CNTT, An toàn thông tin hoặc Kỹ thuật phần mềm.\n- Yêu thích quản trị hệ thống, DevOps, ham học hỏi.\n- Đảm bảo tối thiểu 4 buổi/tuần.',
        '- Hỗ trợ phụ cấp thực tập 5 - 8 triệu VNĐ/tháng.\n- Cơ hội trở thành nhân viên chính thức sau khi tốt nghiệp.',
        '5,000,000 - 8,000,000 VNĐ',
        'Thái Nguyên / Hà Nội',
        'Thực tập',
        'approved',
        '2026-11-20'
      ]
    ];

    const insertedJobIds = [];
    for (const job of jobs) {
      const [res] = await connection.query(
        `INSERT INTO jobs (company_id, category_id, title, description, requirements, benefits, salary_range, location, job_type, status, deadline)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        job
      );
      insertedJobIds.push(res.insertId);
    }

    // 8. Applications
    await connection.query(
      `INSERT INTO applications (job_id, candidate_id, cv_file, cover_letter, status) VALUES
      (?, ?, '/uploads/cvs/CV_TruongThiBichNgoc_DTC245200251.pdf', 'Kính gửi Quý công ty, em là Trương Thị Bích Ngọc - sinh viên CNTT-K23C trường ĐH CNTT&TT Thái Nguyên. Em rất quan tâm đến vị trí DevOps Engineer và mong muốn được cống hiến năng lực của mình.', 'reviewing')`,
      [insertedJobIds[0], cand1Res.insertId]
    );

    await connection.query(
      `INSERT INTO applications (job_id, candidate_id, cv_file, cover_letter, status) VALUES
      (?, ?, '/uploads/cvs/CV_TruongThiBichNgoc_DTC245200251.pdf', 'Em có nền tảng về hệ thống mạng, bảo mật Linux và Nginx reverse proxy. Rất mong có cơ hội phỏng vấn trao đổi.', 'accepted')`,
      [insertedJobIds[2], cand1Res.insertId]
    );

    console.log('[Seeder] Initial data seeding completed successfully!');
  } catch (err) {
    console.error('[Seeder] Error during seeding:', err);
  } finally {
    await connection.end();
  }
}

if (require.main === module) {
  runSeed().then(() => process.exit(0)).catch(err => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = runSeed;
