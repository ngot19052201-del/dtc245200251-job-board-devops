const { query } = require('../config/database');

const candidateController = {
  getProfile: async (req, res) => {
    try {
      const userId = req.session.user.id;
      const users = await query('SELECT full_name, email, phone FROM users WHERE id = ?', [userId]);
      const profiles = await query('SELECT * FROM candidate_profiles WHERE user_id = ?', [userId]);

      res.render('candidate/profile', {
        title: 'Hồ sơ cá nhân - JobBoard',
        userInfo: users[0] || {},
        profile: profiles[0] || {}
      });
    } catch (err) {
      console.error('[Candidate Profile Error]', err);
      res.status(500).send('Lỗi máy chủ khi tải hồ sơ.');
    }
  },

  postProfile: async (req, res) => {
    try {
      const userId = req.session.user.id;
      const { full_name, phone, title, bio, skills, experience, education } = req.body;

      // Update users table
      await query('UPDATE users SET full_name = ?, phone = ? WHERE id = ?', [
        full_name ? full_name.trim() : req.session.user.full_name,
        phone ? phone.trim() : null,
        userId
      ]);
      req.session.user.full_name = full_name.trim();

      // Check if profile exists
      const existing = await query('SELECT id, cv_file FROM candidate_profiles WHERE user_id = ?', [userId]);

      let cvPath = existing.length > 0 ? existing[0].cv_file : null;
      if (req.file) {
        cvPath = `/uploads/cvs/${req.file.filename}`;
      }

      if (existing.length > 0) {
        await query(
          `UPDATE candidate_profiles SET 
            title = ?, bio = ?, skills = ?, experience = ?, education = ?, cv_file = ?
          WHERE user_id = ?`,
          [title || null, bio || null, skills || null, experience || null, education || null, cvPath, userId]
        );
      } else {
        await query(
          `INSERT INTO candidate_profiles (user_id, title, bio, skills, experience, education, cv_file)
          VALUES (?, ?, ?, ?, ?, ?, ?)`,
          [userId, title || null, bio || null, skills || null, experience || null, education || null, cvPath]
        );
      }

      req.session.flash = { type: 'success', message: 'Cập nhật hồ sơ cá nhân thành công!' };
      res.redirect('/candidate/profile');
    } catch (err) {
      console.error('[Update Profile Error]', err);
      req.session.flash = { type: 'danger', message: 'Lỗi khi cập nhật hồ sơ: ' + err.message };
      res.redirect('/candidate/profile');
    }
  },

  getApplications: async (req, res) => {
    try {
      const userId = req.session.user.id;
      const applications = await query(`
        SELECT a.*, j.title as job_title, j.salary_range, j.location, j.job_type,
               c.name as company_name, c.logo as company_logo
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN companies c ON j.company_id = c.id
        WHERE a.candidate_id = ?
        ORDER BY a.created_at DESC
      `, [userId]);

      res.render('candidate/applications', {
        title: 'Lịch sử ứng tuyển - JobBoard',
        applications
      });
    } catch (err) {
      console.error('[Applications Error]', err);
      res.status(500).send('Lỗi máy chủ khi lấy danh sách ứng tuyển.');
    }
  }
};

module.exports = candidateController;
