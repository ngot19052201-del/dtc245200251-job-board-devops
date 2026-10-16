const { query } = require('../config/database');

const adminController = {
  getDashboard: async (req, res) => {
    try {
      const [[{ userCount }]] = await query('SELECT COUNT(*) as userCount FROM users');
      const [[{ candidateCount }]] = await query("SELECT COUNT(*) as candidateCount FROM users WHERE role = 'candidate'");
      const [[{ recruiterCount }]] = await query("SELECT COUNT(*) as recruiterCount FROM users WHERE role = 'recruiter'");
      const [[{ jobCount }]] = await query('SELECT COUNT(*) as jobCount FROM jobs');
      const [[{ pendingJobCount }]] = await query("SELECT COUNT(*) as pendingJobCount FROM jobs WHERE status = 'pending'");
      const [[{ applicationCount }]] = await query('SELECT COUNT(*) as applicationCount FROM applications');

      const recentUsers = await query('SELECT id, role, full_name, email, status, created_at FROM users ORDER BY created_at DESC LIMIT 5');
      const pendingJobs = await query(`
        SELECT j.*, c.name as company_name, cat.name as category_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        JOIN job_categories cat ON j.category_id = cat.id
        WHERE j.status = 'pending'
        ORDER BY j.created_at DESC
        LIMIT 5
      `);

      res.render('admin/dashboard', {
        title: 'Bảng Quản Trị Hệ Thống - Admin',
        stats: {
          userCount,
          candidateCount,
          recruiterCount,
          jobCount,
          pendingJobCount,
          applicationCount
        },
        recentUsers,
        pendingJobs
      });
    } catch (err) {
      console.error('[Admin Dashboard Error]', err);
      res.status(500).send('Lỗi máy chủ khi tải trang Admin');
    }
  },

  getUsers: async (req, res) => {
    try {
      const { role, status } = req.query;
      let where = [];
      let params = [];

      if (role && role !== 'all') {
        where.push('role = ?');
        params.push(role);
      }
      if (status && status !== 'all') {
        where.push('status = ?');
        params.push(status);
      }

      const whereSql = where.length > 0 ? 'WHERE ' + where.join(' AND ') : '';
      const users = await query(`SELECT * FROM users ${whereSql} ORDER BY created_at DESC`, params);

      res.render('admin/users', {
        title: 'Quản lý người dùng - Admin',
        users,
        filter: { role: role || 'all', status: status || 'all' }
      });
    } catch (err) {
      console.error('[Admin Users Error]', err);
      res.status(500).send('Lỗi máy chủ khi lấy danh sách người dùng.');
    }
  },

  postToggleUserStatus: async (req, res) => {
    try {
      const { user_id, current_status } = req.body;
      if (parseInt(user_id, 10) === req.session.user.id) {
        req.session.flash = { type: 'danger', message: 'Bạn không thể tự khóa tài khoản của chính mình!' };
        return res.redirect('/admin/users');
      }

      const newStatus = (current_status === 'active') ? 'locked' : 'active';
      await query('UPDATE users SET status = ? WHERE id = ?', [newStatus, user_id]);

      req.session.flash = {
        type: 'success',
        message: `Đã ${newStatus === 'locked' ? 'khóa' : 'mở khóa'} tài khoản thành công.`
      };
      res.redirect('/admin/users');
    } catch (err) {
      console.error('[Toggle User Status Error]', err);
      req.session.flash = { type: 'danger', message: 'Lỗi cập nhật trạng thái người dùng.' };
      res.redirect('/admin/users');
    }
  },

  getJobs: async (req, res) => {
    try {
      const { status } = req.query;
      let where = [];
      let params = [];

      if (status && status !== 'all') {
        where.push('j.status = ?');
        params.push(status);
      }

      const whereSql = where.length > 0 ? 'WHERE ' + where.join(' AND ') : '';
      const jobs = await query(`
        SELECT j.*, c.name as company_name, cat.name as category_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.id
        JOIN job_categories cat ON j.category_id = cat.id
        ${whereSql}
        ORDER BY j.created_at DESC
      `, params);

      res.render('admin/jobs', {
        title: 'Quản lý tin tuyển dụng - Admin',
        jobs,
        filter: { status: status || 'all' }
      });
    } catch (err) {
      console.error('[Admin Jobs Error]', err);
      res.status(500).send('Lỗi máy chủ khi lấy danh sách việc làm.');
    }
  },

  postApproveJob: async (req, res) => {
    try {
      const { job_id, action } = req.body;
      const validActions = ['approved', 'rejected', 'closed'];
      const newStatus = validActions.includes(action) ? action : 'approved';

      await query('UPDATE jobs SET status = ? WHERE id = ?', [newStatus, job_id]);
      req.session.flash = { type: 'success', message: `Đã cập nhật trạng thái tin thành: ${newStatus}` };
      res.redirect('/admin/jobs');
    } catch (err) {
      console.error('[Admin Approve Job Error]', err);
      req.session.flash = { type: 'danger', message: 'Lỗi khi cập nhật trạng thái tin.' };
      res.redirect('/admin/jobs');
    }
  }
};

module.exports = adminController;
