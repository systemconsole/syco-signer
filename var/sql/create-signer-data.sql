USE `Syslog`;

INSERT INTO `signed` (
  `sign`,
  `message`,
  `signdate`,
  `created`
)
VALUES (
  'DANLIN',
  'Had large amounts of web-scans.',
  '2015-05-03',
  '2015-05-04 13:37'
);

INSERT INTO `trigger` (
  `user`,
  `message_trigger`,
  `status`,
  `created`
)
VALUES (
  'DANLIN',
  'Job `cron.%'' started',
  'DELETE',
  '2015-05-04 13:38'
)