const bcrypt = require('bcryptjs');
const { query } = require('../config/database');

const authController = {
  getLogin: (req, res) => {
    if (req.session.user) return res.redirect('/');
    res.render('auth/login', { title: 'Đăng nhập - JobBoard' });
  },

  postLogin: async (req, res) => {
    const { email, password } = req.body;
    try {
      if (!email || !password) {
        req.session.flash = { type: 'danger', message: 'Vui lòng nhập đầy đủ Email và Mật khẩu.' };
        return res.redirect('/auth/login');
      }

      const users = await query('SELECT * FROM users WHERE email = ?', [email.trim().toLowerCase()]);
      if (users.length === 0) {
        req.session.flash = { type: 'danger', message: 'Email hoặc mật khẩu không chính xác.' };
        return res.redirect('/auth/login');
      }

      const user = users[0];
      if (user.status === 'locked') {
        req.session.flash = { type: 'danger', message: 'Tài khoản của bạn đã bị tạm khóa. Vui lòng liên hệ Quản trị viên!' };
        return res.redirect('/auth/login');
      }

      const isMatch = await bcrypt.compare(password, user.password);
      if (!isMatch) {
        req.session.flash = { type: 'danger', message: 'Email hoặc mật khẩu không chính xác.' };
        return res.redirect('/auth/login');
      }

      // Login success
      req.session.user = {
        id: user.id,
        role: user.role,
        full_name: user.full_name,
        email: user.email
      };

      req.session.flash = { type: 'success', message: `Chào mừng trở lại, ${user.full_name}!` };

      if (user.role === 'admin') return res.redirect('/admin');
      if (user.role === 'recruiter') return res.redirect('/recruiter/dashboard');
      return res.redirect('/');
    } catch (err) {
      console.error('[Auth Error]', err);
      req.session.flash = { type: 'danger', message: 'Lỗi máy chủ trong quá trình xác thực.' };
      res.redirect('/auth/login');
    }
  },

  getRegister: (req, res) => {
    if (req.session.user) return res.redirect('/');
    res.render('auth/register', { title: 'Đăng ký tài khoản - JobBoard' });
  },

  postRegister: async (req, res) => {
    const { role, full_name, email, password, confirm_password, phone, company_name, company_address } = req.body;
    try {
      if (!full_name || !email || !password || !role) {
        req.session.flash = { type: 'danger', message: 'Vui lòng điền đầy đủ các thông tin bắt buộc.' };
        return res.redirect('/auth/register');
      }

      if (password !== confirm_password) {
        req.session.flash = { type: 'danger', message: 'Mật khẩu xác nhận không khớp.' };
        return res.redirect('/auth/register');
      }

      if (password.length < 6) {
        req.session.flash = { type: 'danger', message: 'Mật khẩu phải chứa ít nhất 6 ký tự.' };
        return res.redirect('/auth/register');
      }

      const existing = await query('SELECT id FROM users WHERE email = ?', [email.trim().toLowerCase()]);
      if (existing.length > 0) {
        req.session.flash = { type: 'danger', message: 'Email này đã được đăng ký trong hệ thống.' };
        return res.redirect('/auth/register');
      }

      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(password, salt);

      const assignedRole = (role === 'recruiter') ? 'recruiter' : 'candidate';

      const userResult = await query(
        'INSERT INTO users (role, full_name, email, password, phone, status) VALUES (?, ?, ?, ?, ?, ?)',
        [assignedRole, full_name.trim(), email.trim().toLowerCase(), hashedPassword, phone || null, 'active']
      );

      const newUserId = userResult.insertId;

      if (assignedRole === 'recruiter') {
        const cName = company_name ? company_name.trim() : `Công ty của ${full_name}`;
        const cAddress = company_address ? company_address.trim() : 'Việt Nam';
        await query(
          'INSERT INTO companies (user_id, name, address, description) VALUES (?, ?, ?, ?)',
          [newUserId, cName, cAddress, 'Đang cập nhật thông tin giới thiệu công ty.']
        );
      } else {
        await query(
          'INSERT INTO candidate_profiles (user_id) VALUES (?)',
          [newUserId]
        );
      }

      req.session.user = {
        id: newUserId,
        role: assignedRole,
        full_name: full_name.trim(),
        email: email.trim().toLowerCase()
      };

      req.session.flash = { type: 'success', message: 'Đăng ký tài khoản thành công!' };

      if (assignedRole === 'recruiter') return res.redirect('/recruiter/dashboard');
      return res.redirect('/candidate/profile');
    } catch (err) {
      console.error('[Register Error]', err);
      req.session.flash = { type: 'danger', message: 'Đã có lỗi xảy ra khi tạo tài khoản.' };
      res.redirect('/auth/register');
    }
  },

  logout: (req, res) => {
    req.session.destroy(() => {
      res.redirect('/');
    });
  }
};

module.exports = authController;
