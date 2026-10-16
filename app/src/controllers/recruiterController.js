const { query } = require('../config/database');

const recruiterController = {
  getDashboard: async (req, res) => {
    try {
      const userId = req.session.user.id;
      const companies = await query('SELECT * FROM companies WHERE user_id = ?', [userId]);
      if (companies.length === 0) {
        req.session.flash = { type: 'warning', message: 'Vui lòng cập nhật thông tin công ty của bạn.' };
        return res.redirect('/');
      }
      const company = companies[0];

      // Jobs posted by this company
      const jobs = await query(`
        SELECT j.*, cat.name as category_name, COUNT(a.id) as applicant_count
        FROM jobs j
        JOIN job_categories cat ON j.category_id = cat.id
        LEFT JOIN applications a ON j.id = a.job_id
        WHERE j.company_id = ?
        GROUP BY j.id
        ORDER BY j.created_at DESC
      `, [company.id]);

      // Total applicants across all jobs
      const applicantRows = await query(`
        SELECT COUNT(a.id) as totalApplicants
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        WHERE j.company_id = ?
      `, [company.id]);
      const totalApplicants = (applicantRows && applicantRows[0]) ? applicantRows[0].totalApplicants : 0;

      res.render('recruiter/dashboard', {
        title: 'Quản lý tuyển dụng - ' + company.name,
        company,
        jobs,
        stats: {
          totalJobs: jobs.length,
          totalApplicants: totalApplicants || 0,
          activeJobs: jobs.filter(j => j.status === 'approved').length
        }
      });
    } catch (err) {
      console.error('[Recruiter Dashboard Error]', err);
      res.status(500).send('Lỗi máy chủ khi tải trang quản trị tuyển dụng.');
    }
  },

  getPostJob: async (req, res) => {
    try {
      const categories = await query('SELECT * FROM job_categories ORDER BY name ASC');
      res.render('recruiter/post-job', {
        title: 'Đăng tin tuyển dụng mới - JobBoard',
        categories
      });
    } catch (err) {
      console.error('[Post Job Get Error]', err);
      res.status(500).send('Lỗi máy chủ');
    }
  },

  postPostJob: async (req, res) => {
    try {
      const userId = req.session.user.id;
      const companies = await query('SELECT id FROM companies WHERE user_id = ?', [userId]);
      if (companies.length === 0) {
        req.session.flash = { type: 'danger', message: 'Không tìm thấy thông tin công ty của bạn.' };
        return res.redirect('/recruiter/dashboard');
      }
      const companyId = companies[0].id;

      const { title, category_id, job_type, salary_range, location, deadline, description, requirements, benefits } = req.body;

      if (!title || !category_id || !salary_range || !location || !deadline || !description || !requirements) {
        req.session.flash = { type: 'danger', message: 'Vui lòng nhập đầy đủ các trường bắt buộc.' };
        return res.redirect('/recruiter/post-job');
      }

      await query(
        `INSERT INTO jobs (company_id, category_id, title, description, requirements, benefits, salary_range, location, job_type, status, deadline)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'approved', ?)`,
        [companyId, category_id, title.trim(), description, requirements, benefits || null, salary_range.trim(), location.trim(), job_type, deadline]
      );

      req.session.flash = { type: 'success', message: 'Đăng tin tuyển dụng thành công!' };
      res.redirect('/recruiter/dashboard');
    } catch (err) {
      console.error('[Post Job Post Error]', err);
      req.session.flash = { type: 'danger', message: 'Lỗi khi đăng tin: ' + err.message };
      res.redirect('/recruiter/post-job');
    }
  },

  getEditJob: async (req, res) => {
    try {
      const userId = req.session.user.id;
      const jobId = req.params.id;

      const jobs = await query(`
        SELECT j.* 
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE j.id = ? AND c.user_id = ?
      `, [jobId, userId]);

      if (jobs.length === 0) {
        req.session.flash = { type: 'danger', message: 'Không tìm thấy tin tuyển dụng hoặc bạn không có quyền sửa.' };
        return res.redirect('/recruiter/dashboard');
      }

      const categories = await query('SELECT * FROM job_categories ORDER BY name ASC');
      res.render('recruiter/edit-job', {
        title: 'Chỉnh sửa tin tuyển dụng - JobBoard',
        job: jobs[0],
        categories
      });
    } catch (err) {
      console.error('[Edit Job Get Error]', err);
      res.status(500).send('Lỗi máy chủ');
    }
  },

  postEditJob: async (req, res) => {
    try {
      const userId = req.session.user.id;
      const jobId = req.params.id;
      const { title, category_id, job_type, salary_range, location, deadline, description, requirements, benefits, status } = req.body;

      const jobs = await query(`
        SELECT j.id FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE j.id = ? AND c.user_id = ?
      `, [jobId, userId]);

      if (jobs.length === 0) {
        req.session.flash = { type: 'danger', message: 'Không tìm thấy tin tuyển dụng hoặc bạn không có quyền sửa.' };
        return res.redirect('/recruiter/dashboard');
      }

      await query(
        `UPDATE jobs SET
          title = ?, category_id = ?, job_type = ?, salary_range = ?, location = ?,
          deadline = ?, description = ?, requirements = ?, benefits = ?, status = ?
        WHERE id = ?`,
        [title.trim(), category_id, job_type, salary_range.trim(), location.trim(), deadline, description, requirements, benefits || null, status, jobId]
      );

      req.session.flash = { type: 'success', message: 'Cập nhật tin tuyển dụng thành công!' };
      res.redirect('/recruiter/dashboard');
    } catch (err) {
      console.error('[Edit Job Post Error]', err);
      req.session.flash = { type: 'danger', message: 'Lỗi cập nhật: ' + err.message };
      res.redirect(`/recruiter/edit-job/${req.params.id}`);
    }
  },

  getApplicants: async (req, res) => {
    try {
      const userId = req.session.user.id;
      const jobId = req.query.job_id;

      let sql = `
        SELECT a.*, u.full_name as candidate_name, u.email as candidate_email, u.phone as candidate_phone,
               j.title as job_title, cp.skills, cp.experience
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        JOIN users u ON a.candidate_id = u.id
        LEFT JOIN candidate_profiles cp ON u.id = cp.user_id
        WHERE c.user_id = ?
      `;
      const params = [userId];

      if (jobId) {
        sql += ' AND j.id = ?';
        params.push(jobId);
      }

      sql += ' ORDER BY a.created_at DESC';

      const applicants = await query(sql, params);
      const jobs = await query(`
        SELECT j.id, j.title
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        WHERE c.user_id = ?
      `, [userId]);

      res.render('recruiter/applicants', {
        title: 'Danh sách hồ sơ ứng tuyển - JobBoard',
        applicants,
        jobs,
        selectedJobId: jobId || ''
      });
    } catch (err) {
      console.error('[Recruiter Applicants Error]', err);
      res.status(500).send('Lỗi máy chủ khi lấy danh sách ứng viên.');
    }
  },

  postUpdateApplicationStatus: async (req, res) => {
    try {
      const { application_id, status } = req.body;
      const userId = req.session.user.id;

      // Verify permission
      const apps = await query(`
        SELECT a.id FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE a.id = ? AND c.user_id = ?
      `, [application_id, userId]);

      if (apps.length === 0) {
        req.session.flash = { type: 'danger', message: 'Không tìm thấy hồ sơ hoặc bạn không có quyền xử lý.' };
        return res.redirect('/recruiter/applicants');
      }

      await query('UPDATE applications SET status = ? WHERE id = ?', [status, application_id]);
      req.session.flash = { type: 'success', message: 'Đã cập nhật trạng thái hồ sơ ứng tuyển thành công.' };
      res.redirect('/recruiter/applicants');
    } catch (err) {
      console.error('[Update App Status Error]', err);
      req.session.flash = { type: 'danger', message: 'Lỗi cập nhật: ' + err.message };
      res.redirect('/recruiter/applicants');
    }
  }
};

module.exports = recruiterController;
