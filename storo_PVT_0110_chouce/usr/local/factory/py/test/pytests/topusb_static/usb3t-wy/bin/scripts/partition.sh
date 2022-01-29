# to create the partitions programatically (rather than manually)
# we're going to simulate the manual input to fdisk
# The sed script strips off all the comments so that we can
# document what we're doing in-line with the actual commands
# Note that a blank line (commented as "defualt" will send a empty
# line terminated with a newline to take the fdisk default.
# ${1} sed cmd
# ${2} fdisk cmd
# ${3} target disk
${1} -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' <<EOF | ${2} ${3}
  o # clear the in memory partition table
  n # new partition
  p # primary partition
  1 # partion number 1
    # default, start immediately after preceding partition
    # default, extend partition to end of disk
  p # print the in-memory partition table
  w # write the partition table
  q # and we're done
EOF
