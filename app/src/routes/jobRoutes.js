const express = require('express');
const router = express.Router();
const jobController = require('../controllers/jobController');
const upload = require('../middleware/upload');
const { requireAuth, requireRole } = require('../middleware/auth');

router.get('/', jobController.getHome);
router.get('/jobs', jobController.getJobs);
router.get('/jobs/:id', jobController.getJobDetail);
router.post('/jobs/:id/apply', requireAuth, requireRole('candidate'), upload.single('cv'), jobController.postApply);

module.exports = router;
