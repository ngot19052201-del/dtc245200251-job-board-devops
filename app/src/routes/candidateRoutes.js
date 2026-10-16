const express = require('express');
const router = express.Router();
const candidateController = require('../controllers/candidateController');
const upload = require('../middleware/upload');
const { requireAuth, requireRole } = require('../middleware/auth');

router.use(requireAuth);
router.use(requireRole('candidate'));

router.get('/profile', candidateController.getProfile);
router.post('/profile', upload.single('cv'), candidateController.postProfile);
router.get('/applications', candidateController.getApplications);

module.exports = router;
