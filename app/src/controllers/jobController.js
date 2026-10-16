const { query } = require('../config/database');

const jobController = {
  getHome: async (req, res) => {
    try {
      // 1. Statistics
      const jRows = await query("SELECT COUNT(*) as total FROM jobs WHERE status = 'approved'");
      const cRows = await query("SELECT COUNT(*) as total FROM companies");
      const aRows = await query("SELECT COUNT(*) as total FROM applications");
      const totalJobs = (jRows && jRows[0]) ? jRows[0].total : 0;
      const totalCompanies = (cRows && cRows[0]) ? cRows[0].total : 0;
      const totalApplications = (aRows && aRows[0]) ? aRows[0].total : 0;

      // 2. Categories with job count
      const categories = await query(`
        SELECT c.*, COUNT(j.id) as job_count
        FROM job_categories c
        LEFT JOIN jobs j ON c.id = j.category_id AND j.status = 'approved'
        GROUP BY c.id
        ORDER BY job_count DESC, c.name ASC
      `);

      // 3. Featured / Recent Jobs
      const recentJobs = await query(`
        SELECT j.*, c.name as company_name, c.logo as company_logo, cat.name as category_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        JOIN job_categories cat ON j.category_id = cat.id
        WHERE j.status = 'approved'
        ORDER BY j.created_at DESC
        LIMIT 6
      `);

      // 4. Featured Companies
      const companies = await query(`
        SELECT c.*, COUNT(j.id) as open_jobs
        FROM companies c
        LEFT JOIN jobs j ON c.id = j.company_id AND j.status = 'approved'
        GROUP BY c.id
        LIMIT 4
      `);

      res.render('index', {
        title: 'Cổng Tuyển Dụng & Việc Làm Trực Tuyến - JobBoard',
        stats: { totalJobs, totalCompanies, totalApplications },
        categories,
        recentJobs,
        companies
      });
    } catch (err) {
      console.error('[Home Error]', err);
      res.status(500).send('Lỗi máy chủ nội bộ');
    }
  },

  getJobs: async (req, res) => {
    try {
      const { keyword, category, location, job_type, page = 1 } = req.query;
      const limit = 6;
      const offset = (parseInt(page, 10) - 1) * limit;

      let whereClauses = ["j.status = 'approved'"];
      let params = [];

      if (keyword && keyword.trim() !== '') {
        whereClauses.push('(j.title LIKE ? OR j.description LIKE ? OR c.name LIKE ?)');
        const kw = `%${keyword.trim()}%`;
        params.push(kw, kw, kw);
      }

      if (category && category !== 'all') {
        whereClauses.push('j.category_id = ?');
        params.push(parseInt(category, 10));
      }

      if (location && location.trim() !== '') {
        whereClauses.push('j.location LIKE ?');
        params.push(`%${location.trim()}%`);
      }

      if (job_type && job_type !== 'all') {
        whereClauses.push('j.job_type = ?');
        params.push(job_type);
      }

      const whereSql = whereClauses.length > 0 ? 'WHERE ' + whereClauses.join(' AND ') : '';

      // Count total
      const countSql = `
        SELECT COUNT(*) as total
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        ${whereSql}
      `;
      const countRows = await query(countSql, params);
      const totalJobs = countRows[0].total;
      const totalPages = Math.ceil(totalJobs / limit) || 1;

      // Select jobs with pagination
      const jobsSql = `
        SELECT j.*, c.name as company_name, c.logo as company_logo, cat.name as category_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        JOIN job_categories cat ON j.category_id = cat.id
        ${whereSql}
        ORDER BY j.created_at DESC
        LIMIT ${limit} OFFSET ${offset}
      `;
      const jobs = await query(jobsSql, params);

      // Categories for filter
      const categories = await query('SELECT * FROM job_categories ORDER BY name ASC');

      res.render('jobs/index', {
        title: 'Tìm kiếm việc làm - JobBoard',
        jobs,
        categories,
        filters: { keyword: keyword || '', category: category || 'all', location: location || '', job_type: job_type || 'all' },
        pagination: {
          currentPage: parseInt(page, 10),
          totalPages,
          totalJobs
        }
      });
    } catch (err) {
      console.error('[Jobs List Error]', err);
      res.status(500).send('Lỗi máy chủ khi tìm kiếm việc làm');
    }
  },

  getJobDetail: async (req, res) => {
    try {
      const jobId = req.params.id;
      const jobs = await query(`
        SELECT j.*, c.name as company_name, c.logo as company_logo, c.website as company_website,
               c.address as company_address, c.description as company_description, c.scale as company_scale,
               cat.name as category_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        JOIN job_categories cat ON j.category_id = cat.id
        WHERE j.id = ?
      `, [jobId]);

      if (jobs.length === 0) {
        req.session.flash = { type: 'danger', message: 'Không tìm thấy thông tin tin tuyển dụng này.' };
        return res.redirect('/jobs');
      }

      const job = jobs[0];

      // Check if current user already applied
      let hasApplied = false;
      let candidateProfile = null;
      if (req.session.user && req.session.user.role === 'candidate') {
        const applications = await query(
          'SELECT id FROM applications WHERE job_id = ? AND candidate_id = ?',
          [jobId, req.session.user.id]
        );
        hasApplied = applications.length > 0;

        const profiles = await query('SELECT * FROM candidate_profiles WHERE user_id = ?', [req.session.user.id]);
        if (profiles.length > 0) candidateProfile = profiles[0];
      }

      // Related jobs
      const relatedJobs = await query(`
        SELECT j.*, c.name as company_name, c.logo as company_logo
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE j.category_id = ? AND j.id != ? AND j.status = 'approved'
        LIMIT 3
      `, [job.category_id, jobId]);

      res.render('jobs/detail', {
        title: `${job.title} - ${job.company_name} | JobBoard`,
        job,
        hasApplied,
        candidateProfile,
        relatedJobs
      });
    } catch (err) {
      console.error('[Job Detail Error]', err);
      res.status(500).send('Lỗi khi tải thông tin việc làm');
    }
  },

  postApply: async (req, res) => {
    const jobId = req.params.id;
    try {
      if (!req.session.user) {
        req.session.flash = { type: 'danger', message: 'Vui lòng đăng nhập với tư cách Ứng viên để nộp hồ sơ.' };
        return res.redirect('/auth/login');
      }

      if (req.session.user.role !== 'candidate') {
        req.session.flash = { type: 'danger', message: 'Chỉ tài khoản Ứng viên mới có thể nộp đơn ứng tuyển.' };
        return res.redirect(`/jobs/${jobId}`);
      }

      const candidateId = req.session.user.id;

      // Check if already applied
      const existing = await query('SELECT id FROM applications WHERE job_id = ? AND candidate_id = ?', [jobId, candidateId]);
      if (existing.length > 0) {
        req.session.flash = { type: 'warning', message: 'Bạn đã nộp hồ sơ ứng tuyển cho vị trí này rồi.' };
        return res.redirect(`/jobs/${jobId}`);
      }

      let cvPath = null;
      if (req.file) {
        cvPath = `/uploads/cvs/${req.file.filename}`;
      } else {
        // Use existing profile CV
        const profiles = await query('SELECT cv_file FROM candidate_profiles WHERE user_id = ?', [candidateId]);
        if (profiles.length > 0 && profiles[0].cv_file) {
          cvPath = profiles[0].cv_file;
        }
      }

      if (!cvPath) {
        req.session.flash = { type: 'danger', message: 'Vui lòng tải lên tệp CV của bạn (PDF/DOCX).' };
        return res.redirect(`/jobs/${jobId}`);
      }

      const coverLetter = req.body.cover_letter || '';

      await query(
        'INSERT INTO applications (job_id, candidate_id, cv_file, cover_letter, status) VALUES (?, ?, ?, ?, ?)',
        [jobId, candidateId, cvPath, coverLetter, 'submitted']
      );

      req.session.flash = { type: 'success', message: 'Nộp hồ sơ ứng tuyển thành công! Nhà tuyển dụng sẽ sớm liên hệ với bạn.' };
      res.redirect('/candidate/applications');
    } catch (err) {
      console.error('[Apply Error]', err);
      req.session.flash = { type: 'danger', message: 'Có lỗi xảy ra khi nộp hồ sơ: ' + err.message };
      res.redirect(`/jobs/${jobId}`);
    }
  }
};

module.exports = jobController;
