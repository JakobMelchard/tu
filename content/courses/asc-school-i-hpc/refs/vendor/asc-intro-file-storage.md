---
title: |
  \textcolor{red}{Storage Infrastructure on ASC}
---

### $HOME Fileystem

- IBM Spectrum Scale File System
- Used for software and job scripts
- All NVMe storage
- Quotas
  - 100 GB (strict)
  - 10^6 inodes
- Accessible with **$HOME** environment variable
  - /home/fs70XXX/username
  logo{ style="width: 70%; margin: auto;" }

### $DATA Fileystem

- IBM Spectrum Scale File System
- Can be used for most kind of I/O
- Tiered storage
- Quotas
  - 100 GB (can be extanded on request)
  - 10^6 inodes
- Accessible with **$DATA** environment variable
  - /gpfs/data/fs70XXX/username
  logo{ style="width: 70%; margin: auto;" }

### $DATA Tiering

- Spectrum Scale policy



### Local Fileystem

- Should be used for local I/O
- 480 GB local SSD (VSC-4)
- 2 TB local NVMe (VSC-5)
- Accessible on compute nodes
  - /local
- Data gets deleted after the job
  - Write results to **%DATA** to make data persistent

### TMP Filesystem

- Can be used for heavy local I/O
- Up to half of the nodes memory
  - ** Data resides in the shared memory (RAM) of the node **
- Accessible on compute nodes
  - /tmp
- Data gets deleted after the job
  - Write results to **%DATA** to make data persistent

### Backup Policy

- Backups of user files is solely managed by the user
- Backups are used for disaster recovery only
- Backups are performed on the best effort basis
- Backed up filesystems:
  - $HOME
  - $DATA
- Project manager can exclude $DATA filesystem from backups
  - service.asc.ac.at
- Setup continuous backups of user data to remote Machines
  - documentation: https://docs.vsc.ac.at/storage/backup.html


### Copy and sync



### Copy - alternative via FileZilla



### Copy - alternative via WinSCP

<<<<<<< HEAD

=======

>>>>>>> 61a15f7c77e2dba0f36730c9dde2aafd4d86d19f
