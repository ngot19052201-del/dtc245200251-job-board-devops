const express = require('express');
const router = express.Router();
const adminController = require('../controllers/adminController');
const { requireAuth, requireRole } = require('../middleware/auth');

router.use(requireAuth);
router.use(requireRole('admin'));

router.get('/', adminController.getDashboard);
router.get('/users', adminController.getUsers);
router.post('/users/toggle-status', adminController.postToggleUserStatus);
router.get('/jobs', adminController.getJobs);
router.post('/jobs/approve', adminController.postApproveJob);

module.exports = router;
