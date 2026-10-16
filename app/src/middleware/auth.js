// Authentication & Authorization Middleware

function attachUser(req, res, next) {
  res.locals.user = req.session ? req.session.user : null;
  res.locals.flash = req.session ? req.session.flash : null;
  if (req.session && req.session.flash) {
    delete req.session.flash;
  }
  next();
}

function requireAuth(req, res, next) {
  if (!req.session || !req.session.user) {
    req.session.flash = { type: 'danger', message: 'Vui lòng đăng nhập để tiếp tục.' };
    return res.redirect('/auth/login');
  }
  next();
}

function requireRole(allowedRoles) {
  return (req, res, next) => {
    if (!req.session || !req.session.user) {
      req.session.flash = { type: 'danger', message: 'Vui lòng đăng nhập để thực hiện chức năng này.' };
      return res.redirect('/auth/login');
    }
    const userRole = req.session.user.role;
    const roles = Array.isArray(allowedRoles) ? allowedRoles : [allowedRoles];
    if (!roles.includes(userRole)) {
      req.session.flash = { type: 'danger', message: 'Bạn không có quyền truy cập khu vực này.' };
      return res.redirect('/');
    }
    next();
  };
}

module.exports = {
  attachUser,
  requireAuth,
  requireRole
};
