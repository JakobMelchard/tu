---
author: ASC Research Center, TU Wien
title: Linux Intro
---date: \today
date: March 2, 2026
---


### Timetable

4 parts, each:

- Lecture

- Exercise

- Demonstration

- Break

Lunchbreak from 12 to 1 pm.

Questions? Always!


<!---
### Operating Systems

Vote: What's your **operating systems**?

- **Linux**

- **macOS**

- **Windows**
-->


### Why Linux?

{height=80% style="float: right;"}


### What do you know about Linux?

{height=80% style="float: 'right';"}
<!---
By a show of hands:

- Nothing

- Terminal and command line

- Files and directories

- Permissions

- Variables

- Streams

- Shell scripts
-->

### Terminal & Prompt

Welcome to a **terminal** showing the default `bash prompt`.

```{.bash .numberLines startFrom="1"}
myenv myuser@mymachine: mylocation$
skylake trainee00@l44:~$
zen trainee00@l55:~/mydir$
```

All the `typewriter` text, and all dark grey boxes mean **code**.

Lines that start with a `"$"` means a **command in a terminal**.


### Execution

To execute a command or run a program, we **call** it.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ whoami
trainee00

zen trainee00@l55:~$ echo "hello world"
hello world

zen trainee00@l55:~$ cp file1 file1_copy   # copies source to destination

zen trainee00@l55:~$ /bin/python

zen trainee00@l55:~$ ./myscript.sh    # executes myscript.sh
```


### History

Type `history` for a log of all the commands you executed so far.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ history
whoami
echo "hello world"
cp file1 file1_copy
/bin/python
./myscript.sh
```

For the last commands try `<Up-Arrow>`, or type `<CTRL>-R` to search
for keyword.


### Completion

Type `<TAB>` when you enter a command to get **suggestions**.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ e<TAB>
e2freefrag             env                    eu-elflint
e2fsck                 envsubst               eu-findtextrel
e2image                eodc_commands.py       eu-make-debug-archive
...
```

If there is only one possible match, it gets **completed**.

```{.bash .numberLines startFrom="6"}
zen trainee00@l55:~$ ec<TAB>
echo
```


### Parameters/Flags

Give your program more info: write parameters **following** the
program name.

1. Single-character with dash
   ```{.bash .numberLines startFrom="1"}
   zen trainee00@l55:~$ mycommand -a -b -c -d -e
   zen trainee00@l55:~$ ls -1alh
   ```
2. Multi-character with double dash
   ```{.bash .numberLines startFrom="3"}
   zen trainee00@l55:~$ mycommand --flag-parameter=flag-value
   zen trainee00@l55:~$ ls --color=always
   ```
3. Strings
   ```{.bash .numberLines startFrom="6"}
   zen trainee00@l55:~$ mycommand mysource mydestination
   zen trainee00@l55:~$ cp myoldfile mynewfile
   ```


### Order

Run **from** the source **to** the destination.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ mycommand mysource mydestination    # ok
zen trainee00@l55:~$ cp file1 file1_copy                 
```
Keep parameters and their arguments **together**.
```{.bash .numberLines startFrom="3"}
zen trainee00@l55:~$ mycommand -j 2 --color auto    # ok
zen trainee00@l55:~$ mycommand -j auto --color 2    # probably wrong
```

**Beware**, the spaces between program name and parameter are important.


### Filesystem

The filesystem has different **objects**.

- Files

- Directories




### Path

Everything starts at the **root directory** `"/"`.

```{.bash .numberLines startFrom="1"}
/
/home/fs70824/trainee00
/home/lv70824/trainee00/mydir
```

Objects can be referenced by their **absolute** or **relative** path.
```{.bash .numberLines startFrom="4"}
/home/fs70824/trainee00/mydir/myfile
mydir/myfile
./myfile       # in this directory
../myfile      # in the directory above
```


### Exercise 1

- [ ] Start a **terminal** and login to **VSC**

- [ ] What machine are you on?

- [ ] Run these **commands** (without the `"$"`):

    ```{.bash .numberLines startFrom="1"}
    zen trainee00@l55:~$ man
    zen trainee00@l55:~$ man man
    zen trainee00@l55:~$ echo "hello world"
    ```

- [ ] Use **completion** to find out what this command could be:

   ```{.bash .numberLines startFrom="4"}
    zen trainee00@l55:~$ whoa
    ```

- [ ] View your command **history**

- [ ] **Search** for the `echo` command in your history

### Navigation

1. Look around
    1. `ls`     - List directory contents
    2. `ll`     - Detailed listing (`ls -l`)
    3. `ls -a`  - List including hidden files
2. Move around
    1. `pwd`           - Print working directory
    2. `cd ..`         - Move to parent directory
    3. `cd /dir1/dir2` - Move to specific directory

### File Operations

1. Create files
   1. `mkdir` - Create directory
   2. `touch` - Create empty file
2. View Files
   1. `cat`  - Concatenate and display files
   2. `less` - View file content page by page
   3. `head` - Display first lines of a file
   4. `tail` - Display last lines of a file
3. Change/Delete Files
   1. `mv` - Move or rename files
   2. `cp` - Copy files
   3. `rm` - Remove files

### Input/Output Control

1. Redirects
   1. `>`  - Redirect output (overwrite)
   2. `>>` - Redirect output (append)
   3. `<`  - Redirect input

### System Operations

1. Find
   1. `grep`      - Search text using patterns
   2. `find`      - Search for files in directory hierarchy
   3. `man`       - Display manual pages
   4. `Wildcard`  - Display files matching wildcard pattern
2. Monitor
   1. `top`  - Display Linux processes
   2. `htop` - Interactive process viewer
3. Transfer
   1. `scp`     - Secure copy (remote file copy)
   2. `rsync`   - Remote file synchronization
   3. FileZilla - GUI FTP client
   4. WinSCP    - Windows GUI SCP client

### Navigation:- Look Around

Type `ls` (list) to **look around**.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ ls
all_numbers_from_to.sh  delete_me_empty     delete_me_recursive
```

```{.bash .numberLines startFrom="3"}
zen trainee00@l55:~$ ls -a
.   delete_me_empty      empty_dir      one_string_two_words.sh
..  delete_me_nonempty   fizz_buzz.c    .found_me_hiding.txt
```


### Navigation:- Move Around

Type `pwd` (print working directory) to see your **current
position**.

```{.bash .numberLines startFrom="1"}
trainee00@l44:~$ pwd
/home/fs70824/trainee00
```

Type `cd` (change directory) to **move around**.

```{.bash .numberLines startFrom="3"}
zen trainee00@l55:~$ cd /bin
zen trainee00@l55:~$ cd mydir
zen trainee00@l55:~$ cd ..              # go to parent directory
zen trainee00@l55:~$ cd ~               # go home
zen trainee00@l55:~$ cd -               # go to previous directory
```


### File Operation:- Create

Type `mkdir` to **make** a new directory.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ mkdir mynewdir
```

Type `touch` **create** an empty file.

```{.bash .numberLines startFrom="2"}
zen trainee00@l55:~$ touch mynewfile           # create empty file
```

There are many more ways to write to files.


### File Operations:- View

Type `cat` to **concatenate** textfiles, and print into the terminal.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ cat myfile
zen trainee00@l55:~$ cat myfile1 myfile2 myfile3 ...
```

Like all text you can redirect the concatenated result to a file with
`">"`.


### File Operations:- View

Type `less` to **view** a text file.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ less myfile.txt    # exit with "q"
```

Type `head` to view the **beginning** of a text file.

```{.bash .numberLines startFrom="2"}
zen trainee00@l55:~$ head myfile.txt
```

Type `tail` to view the **end** of a text file.

```{.bash .numberLines startFrom="3"}
zen trainee00@l55:~$ tail myfile.txt
```

### File Operations: Change/Delete 

Type `mv` to **move stuff**.
```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ mv myfile mydir/     # move myfile into mydir
zen trainee00@l55:~$ mv mydir1/ mydir2/   # move whole mydir1 into mydir2
zen trainee00@l55:~$ mv myold mynew       # rename myold to mynew
zen trainee00@l55:~$ mv myfile1 myfile2   # overwrite myfile2 with myfile1 (BEWARE)

```

Type `cp` to **copy stuff**.
```{.bash .numberLines startFrom="5"}
zen trainee00@l55:~$ cp myinput myinput.bak   # copy input to input.bak
zen trainee00@l55:~$ cp myinput mybackup/     # copy input into backup dir
zen trainee00@l55:~$ cp -r mydir1/ mydir2     # copy whole dir1 into dir2
```


### File Operations:- Change/Delete

Type `rmdir` to **remove** an empty directory.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ rmdir myemptydir 
```

Type `rm` to **remove** stuff, be careful!

```{.bash .numberLines startFrom="2"}
zen trainee00@l55:~$ rm myfile
zen trainee00@l55:~$ rm -r mynonemptydir/
zen trainee00@l55:~$ rm -f myfile           # force, beware!
```

### Input/Output Control:- Redirects

Use `">"` to redirect, or `">>"` to append **output** stream to a
**file**.

```{.bash .numberLines startFrom="1"}
mycommand > mystd.log      # redirect "stdout" to a file
mycommand >> mystd.log     # append "stdout" to a file
mycommand 2> myerr.log     # redirect "stderr" to a file
mycommand 2>> myerr.log    # append "stderr" to a file
mycommand 2>&1             # redirect "stderr" to "stdout"
```

Use `"<"` to redirect a **file** to the **input** stream of a program.

```{.bash .numberLines startFrom="6"}
mycommand < myconfig       # redirect a file to "stdin"
```

### Transfer:- Remote Copy

Use `scp` (secure copy) on your local machine to copy files
**to/from** a remote machine.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ scp mysource mydestination
zen trainee00@l55:~$ scp mylocalfile trainee00@vsc5.vsc.ac.at:myvscfile
zen trainee00@l55:~$ scp -r mylocaldir trainee00@vsc5.vsc.ac.at:myvscdir
zen trainee00@l55:~$ scp trainee00@vsc5.vsc.ac.at:myvscfile mylocalfile
```

Use `"-r"` to copy whole **directories** to/from.


### Transfer:- Remote Sync

Use `rsync` (remote sync) on your local machine to **synchronise**
files with remote machine. Rsync is like a more complicated but more
powerful `scp`.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ rsync myoptions mysource mydestination
zen trainee00@l55:~$ rsync mylocalfile trainee00@vsc5.vsc.ac.at:myvscfile
zen trainee00@l55:~$ rsync trainee00@vsc5.vsc.ac.at:myvscfile mylocalfile
zen trainee00@l55:~$ rsync -a mylocaldir/ trainee00@vsc5.vsc.ac.at:myvscdir
```

The flag `"-a"` (archive) syncs whole directories recursively yet
preserves symbolic links, special and device files, modification
times, groups, owners, and permissions, but needs root.

Without the trailing slash in `mylocaldir/` rsync places the whole
directory inside the remote directory `myvscdir/mylocaldir/myfiles`.


### Transfer:- Remote Sync

Use the `"-n"` flag with `rsync` to test your command without copying
anything.

```{.bash .numberLines startFrom="1"}
$rsync -anv mylocaldir/ myvscdir

sending incremental file list
./
myfile1
myfile2
myfile3
...
```

Use the `"-v"` flag (verbose) with `rsync` to get more information.


### Transfer:- Filezilla

**Beware**, always use `Logon Type interactive`.

{height=80% style="float: right;"}


### Transfer:- WinSCP

{height=80% style="float: right;"}


### System Operations:- Search

Use `grep` to **search** for patterns in text.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ grep foo myfile
zen trainee00@l55:~$ grep bar myfile1 myfile2 myfile3
zen trainee00@l55:~$ grep -r baz mydir/
zen trainee00@l55:~$ grep "if" fizz_buzz.c
zen trainee00@l55:~$ grep -r "a" ~
```

### System Operations:- Search

Use `find` to **find** for files, directories, etc.

```{.bash .numberLines startFrom="1"}
## find syntax
zen trainee00@l55:~$ find [path...] [expression]       
## Find files named "config.txt" in current directory 
zen trainee00@l55:~$ find . -name "config.txt"        
## Find files with .txt extension (case-sensitive) 
zen trainee00@l55:~$ find /home -name "*.txt"         
## Find directories named "Documents"
zen trainee00@l55:~$ find ~ -type d -name "Documents"  
```

Type "man find" to read the **manual** specific to the find command.

### System Operations:- Search

Type `man` to read the **manual**.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ man man
zen trainee00@l55:~$ man grep
zen trainee00@l55:~$ man rsync
```

Type `"/"` to **search** for keyword within man, `"h"` for **help** or
`"q"` to **quit**.

### System Operations:- Search

Use `"*"` or a `wildcard` as a placeholders for **any number** of characters.

Use `"?"` for **any single** character.

```{.bash .numberLines startFrom="1"}
# list all pdf files
zen trainee00@l55:~$ ls *.pdf         
# read readme regardless of file type
zen trainee00@l55:~$ less readme.???  
# copy eveything into mydir
zen trainee00@l55:~$ cp * mydir/      
```

There are a lot of others, like `"^"` or `"$"` for beginning and end.


### Exercise 2

- [ ] Look around

- [ ] Copy setup script & run it with your **surname**:

    ```{.bash .numberLines startFrom="1"}
    zen trainee00@l55:~$ cp ~training/vsc_linux_intro.sh ~
    zen trainee00@l55:~$ bash ~/vsc_linux_intro.sh myname
    ```

- [ ] Move into `vsc_linux_intro_myname`

- [ ] Make a directory `foo`

- [ ] Delete the directory `delete_me_empty`

- [ ] Delete the directory `delete_me_nonempty` with the help of **man**

- [ ] Copy the `vsc_linux_intro_myname` to your computer with **scp**


### Ownership and Permissions

Type `ls -lh` to **view** ownership and permissions of stuff.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ ls -lh
permission # user     group  size date   time  name
drwxr-xr-x 4 training p70824 4.0K Feb 23 19:41 empty_dir
lrwxrwxrwx 1 training p70824   11 Feb 23 19:41 link... -> ./empty_dir
-rw-r--r-- 1 training p70824  375 Feb 23 19:41 fizz_buzz.c
...
```

Here `rwxr-xr-x` means the **permissions**, with **r**ead, **w**rite,
   e**x**ecute.

1. `user` can `rwx`
2. `group` can `rx`
3. `others` can `rx`

Here all belongs to the is the **user** `training` (owner) and the
**group** `p70824`.


<!-- ### Ownership -->

<!-- Type `chown` (change owner) to change **ownership** of stuff. -->

<!-- ```{.bash .numberLines startFrom="1"} -->
<!-- zen trainee00@l55:~$ chown myuser myfile -->
<!-- zen trainee00@l55:~$ chown -R myuser:mygroup mydir -->
<!-- zen trainee00@l55:~$ chown me foo.cc -->
<!-- ``` -->


### Permissions

Type `chmod` (change mode) to **change** permissions of stuff.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ chmod myoption myfile
zen trainee00@l55:~$ chmod -R myoption mydir
zen trainee00@l55:~$ chmod +x myexecutable
zen trainee00@l55:~$ chmod u=rwx,g+x,o-rwx myfile
```

Where `u,g,o` means **u**ser, **g**roup and **o**thers.


### Size & Space

Type `du` (disk usage) to view the **size** of stuff.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ du mydir
zen trainee00@l55:~$ du -h myfile1 myfile2    # human readable output
zen trainee00@l55:~$ du -s mydir              # summarize
```

Type `df` (disk free) to view the **free space** of the whole system.

```{.bash .numberLines startFrom="4"}
zen trainee00@l55:~$ df
zen trainee00@l55:~$ df -h        # human readable output
```

**Beware**, you cannot have more files than the **maximum number** of
files at `VSC`!

```{.bash .numberLines startFrom="6"}
zen trainee00@l55:~$ df -ih       # inodes == number of files
```


### Pipe

Use `"|"` to write output stream **into** the input stream of another
process.

```{.bash .numberLines startFrom="1"}
mycommand1 | mycommand2
mycommand1 | mycommand2 | mycommand3 | ...
mycommand | grep foo      # pipe "stdout" into "grep"
df -h | grep data         # show disk free of data fs
ls | grep "foo" | head    # first "foo" in current dir
```


### Manipulate Streams

Use `sed` (stream editor) to manipulate text, like **substitute
words**.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ mycommand | sed "myoption"
# replace foo with bar
zen trainee00@l55:~$ mycommand | sed "s/foo/bar/"    
```

Use `awk` to manipulate structured text, like show **columns**.
```{.bash .numberLines startFrom="3"}
# syntax: awk '{myoption}'
zen trainee00@l55:~$ mycommand | awk '{myoption}'
# print column 2 of every line
zen trainee00@l55:~$ ls -l | awk '{print $1}'            
# print hello, column 5 and 3
zen trainee00@l55:~$ df | awk '{print "hello", $5, $3}'  
```


### Escapes & Quotes

1. Backslash escape:

   Escapes a single character, that would have a special meaning.

   ```{.bash .numberLines startFrom="1"}
   zen trainee00@l55:~$ mycommand this\ is\ a\ single\ parameter
   ```
2. "Double Quotes":

   Does some **wordmagic**: Escape all whitespace characters, expand
   variables, etc.

   ```{.bash .numberLines startFrom="2"}
   zen trainee00@l55:~$ mycommand "$HOME will be /home/myuser"
   ```
3. 'Single Quotes':

   Every character is treated **literally**.

   ```{.bash .numberLines startFrom="3"}
   zen trainee00@l55:~$ mycommand '$HOME will be $HOME'
   ```


### Variables

Use `"="` without space to **set** information as a variable.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ myvar=myvalue
zen trainee00@l55:~$ foo=bar
```

Now use `"$"` to **get** a variable.

```{.bash .numberLines startFrom="3"}
zen trainee00@l55:~$ mycommand $myvar
zen trainee00@l55:~$ echo $foo
```

**Beware**, bash variables are untyped! No `int/float/real/dble`; all
are `string`.


### Environment Variables

**Environment variables** are visible for all programs.

Use `export` to **set** a variable as environment variable.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ export myvar=myvalue
zen trainee00@l55:~$ export LANG=en_US.UTF-8
```

**Beware** if this variable already exists, you **overwrite** it!

```{.bash .numberLines startFrom="3"}
export PATH="$HOME/bin/:$PATH"
```

Overwrite `PATH` to **add** a directory with your programs/scripts.


### Environment Variables

Type `env` to **view** all set an environment variable.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ env
```

Now use `"$"` to **get** an environment variable.

```{.bash .numberLines startFrom="2"}
zen trainee00@l55:~$ mycommand $myvar
zen trainee00@l55:~$ echo $LANG
```

Use `unset` or `env -u` to **delete** an environment variable.

```{.bash .numberLines startFrom="4"}
unset LANG    # no "$" here!
env -u LANG   # no "$" here!
```


### Environment Variables

Some exemplary environment variables:

```{.bash .numberLines startFrom="1"}
HOME              # home directory
PATH              # program paths, in priority order
LIBRARY_PATH      # libraries to link by the compiler
LD_LIBRARY_PATH   # libraries to link at runtime
```

### Monitoring:- Top

Type `top` to watch all **processes**.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ top
Tasks: 650 total,   3 running, 605 sleeping,  42 stopped,   0 zombie
%Cpu(s):  5.3 us,  0.8 sy,  0.0 ni, 94.0 id,  0.0 wa,  0.0 hi,
KiB Mem : 65770984 total,  9477932 free,  9133728 used, 47159324
KiB Swap:        0 total,        0 free,        0 used. 52517312
  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+
20259 trainee00 20   0  258224 101832   7456 R 100.0  0.2   0:58.93
19237 trainee00 20   0  249252  88808   9484 R  84.0  0.1   5:58.72
...
```

Type `h` to get **help** within top: like how to filter for a user.


### Monitoring:- Top Cores

Type `1t` within top to watch all **cores**.

```{.bash .numberLines startFrom="1"}
top - 15:59:40 up 55 days,  7:02, 18 users,  load average: 2.75, 2.76, 2.87
Tasks: 541 total,   2 running, 538 sleeping,   1 stopped,   0 zombie
%Cpu0  :   5.6/9.0    15[|||||||||||                                                                   ]
%Cpu1  :   8.4/15.2   24[|||||||||||||||||||                                                           ]
%Cpu2  :   7.3/12.6   20[||||||||||||||||                                                              ]
%Cpu3  :   5.6/11.6   17[|||||||||||||                                                                 ]
%Cpu4  :   3.3/7.3    11[|||||||||                                                                     ]
```



### Exercise 3

- [ ] Write your name into a text file `myname` using `echo`

- [ ] What is the size of **all** the files in this directory?

- [ ] How much space is left on your `$HOME` and on the `/home` file
      system?

- [ ] Delete **jpg** files inside directory `delete_only_jpg` **at
      once**

- [ ] Combine the files inside directory `cat_together` to **one** new
      file

- [ ] Write your name in the file `try_to_write_to_me`

- [ ] Define the **variable** `NAME` using your surname

- [ ] Export `NAME` as an **environment variable**

- [ ] Delete the **environment variable** `NAME`


### Editors

Editors can

- Read and write

- Copy and paste

- Search and replace

Examples

- `nano`: simple and super easy

- `emacs`: a lot of magic using `<CTRL> <ALT> <SHIFT>`

- `vim`: every letter is a command (complicated)


### Nano

::::: columns
::: column

Use `nano` if you are new to linux.

- **search** with `<CTRL>-W`

- **search & replace** with `<CTRL>-\`

- **cut** line with `<CTL>-K`

- **paste** line with `<CTL>-U`

- **undo** with `<ALT>-U`

- **save & quit** with `<CTRL>-x`

:::
::: column

{height=50% style="float: right;"}

:::
:::::

### Vim

::::: columns
::: column

Use `vim` if you find `emacs` boring.

1. | Type `<ESC>` to go into normal mode
   | **Every letter** you type is a ** command**!

2. | Type `i` for insert mode
   | A **letter** is just a **letter**

3. | Type `":"` for command mode
   | Enter your command to **execute**

:::
::: column

{height=50% style="float: right;"}

:::
:::::


### Vim

Vim examples

- **delete** with `d`

- **search** with `"/" foo`

- **undo** with `u`

- **find and replace** with `":" s/foo/bar/c`

- **save** with `":" w`

- **quit** with `":" q`


### Emacs

::::: columns
::: column

Use `emacs` if you find `nano` boring.

- **search** with `<CTRL>-s`

- **stop** with `<CTRL>-g`

- **undo** with `<CTRL>-"/"`

- **find and replace** with `<ESC> %`

- **save** with `<CTRL>-x <CTRL>-s`

- **quit** with `<CTRL>-x <CTRL>-c`

:::
::: column

{height=50% style="float: right;"}

:::
:::::


### Scripting

Write a shell script to run a **sequence of commands**, like a cooking recipe.

```{.bash .numberLines startFrom="1"}
#!/bin/bash

echo "foo bar"

mkdir mydir
```

Call `bash` to execute a shell script.

```{.bash .numberLines startFrom="6"}
zen trainee00@l55:~$ bash myscript.sh
```

Use `chmod +x`, then call your script directly with `./myscript`.


### Scripting

Like a cooking recipe, your shell script will **continue**, even if a
command **fails**.

```{.bash .numberLines startFrom="1"}
#!/bin/bash

## create a new empty directory (probable already exists):
mkdir .cache

## go to that new directory:
cd .cache

## print whats there, should be empty:
ls .cache/
```

If you execute this bash script, what will happen?


### Shebang

Write a shebang in the first line of your script to tell the shell
your **language**.

```{.bash .numberLines startFrom="1"}
#!/bin/mylanguage
echo "written in foo"
```

```{.bash .numberLines startFrom="3"}
#!/bin/bash
echo "written in bash"
```

```{.python .numberLines startFrom="5"}
#!/bin/python
print "written in python"
```


### Loop

Use **loops** in bash scripts to loop over files, numbers.

```{.bash .numberLines startFrom="1"}
for i in *
do
  echo $i
done
```

```{.bash .numberLines startFrom="5"}
while true
do
  echo "annoying hello world"
  sleep 1
done
```

Or even in **one line**, separated by semicolons, in terminal.

```{.bash .numberLines startFrom="10"}
zen trainee00@l55:~$ for i in {1..5}; do echo $i; done
```


### Expansion

Use **brace expansion** in bash to, well, expand braces.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ echo {a,b,c}1
a1 b1 c1

zen trainee00@l55:~$ echo a{1..9}z
a1z a2z a3z a4z a5z a6z a7z a8z a9z

zen trainee00@l55:~$ echo {a..z}
a b c d e f g h i j k l m n o p q r s t u v w x y z
```


### If/else

Use `if/else` in bash scripts to make quick **yes/no** decisions.

```{.bash .numberLines startFrom="1"}
if [ $myvariable == 0 ]
then
    mycommand1
elif [ $myvariable == 1 ]
then
    mycommand2
else
    mycommand3
fi
```


### Case

Use `case` in bash scripts when a single variable can **many values**.

```{.bash .numberLines startFrom="1"}
case $myvariable in
    0)
        mycommand1
        ;;
    a)
        mycommand2
        ;;
    *)
        mycommand3
        ;;
esac
```

### Function


Define a bash **function** with `myfunction ()`:

```{.bash .numberLines startFrom="1"}
all_numbers_from_to () {
  min=$1
  max=$2
  for num in $(seq $min $max)
  do
    echo "${num}"
  done
}
```

Type `source all_numbers_from_to.sh` to import this function to your
current shell.

Type `all_numbers_from_to 1 10` to run this function, what will
happen?


### Exercise 4

- [ ] Write your name in a file using **nano**

- [ ] **Read & run** the shell script `all_numbers_from_to.sh`

- [ ] **Read & run** the shell script `one_string_two_words.sh`

- [ ] Test different `for j in ...` in `one_string_two_words.sh` using **nano**

- [ ] Write a shell script that **makes a directory** `foobar`

- [ ] Write a shell script that **makes 100 files**



### Documentation

For information about using the clusters visit the ASC documentation!

[https://docs.asc.ac.at/](https://docs.asc.ac.at/)


## Bonus Content

### Alias

Use `alias` to define an **abbreviation** for commands.

```{.bash .numberLines startFrom="1"}
zen trainee00@l55:~$ alias myalias='mycommand myoptions'
zen trainee00@l55:~$ alias ll='ls -alh'
zen trainee00@l55:~$ alias rm='rm -i'
```
<!---zen trainee00@l55:~$ alias myproject='cd $myprojectdir; make && ./myproject' -->

Now you can use the **alias** instead.

```{.bash .numberLines startFrom="4"}
zen trainee00@l55:~$ ll           # Same as "ls -alh"
zen trainee00@l55:~$ rm           # Same as "rm -i"
```
<!--- zen trainee00@l55:~$ myproject    # Same as "cd $myprojectdir; make && ./myproject" -->

Type `alias` to show all **defined** aliases.


### .bashrc

Write a **.bashrc** in your `$HOME`, a script that gets executed
every time you log in.

```{.bash .numberLines startFrom="1"}
#!/bin/false

# define aliases
alias l='ls -1Bhl'
alias sq='squeue -u $USER'
alias rm='rm -i'

# add your own binary directory
export PATH="$PATH:$HOME/bin"
```

An **example** is available at `~training/bashrc_recommended`

Call `source ~/.bashrc` to reload changes.



