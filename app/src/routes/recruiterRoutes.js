const express = require('express');
const router = express.Router();
const recruiterController = require('../controllers/recruiterController');
const { requireAuth, requireRole } = require('../middleware/auth');

router.use(requireAuth);
router.use(requireRole('recruiter'));

router.get('/dashboard', recruiterController.getDashboard);
router.get('/post-job', recruiterController.getPostJob);
router.post('/post-job', recruiterController.postPostJob);
router.get('/edit-job/:id', recruiterController.getEditJob);
router.post('/edit-job/:id', recruiterController.postEditJob);
router.get('/applicants', recruiterController.getApplicants);
router.post('/application-status', recruiterController.postUpdateApplicationStatus);

module.exports = router;
