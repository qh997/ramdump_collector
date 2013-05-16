#!/usr/bin/python

import argparse
import os
import time
import datetime
import tarfile

WORK_PATH = os.getcwd()
TMP_PATH = os.path.join(WORK_PATH, 'myramdump')
BN_PROP = 'ro.build.version.incremental'

def init():
    parser = argparse.ArgumentParser(
        description = 'Collect the ramdump files.',)

    parser.add_argument(
        '-a', '--adb_path',
        default = 'adb',
        help = 'Specify the adb path.(default: %(default)s)')
    parser.add_argument(
        '-o', '--out_path',
        default = WORK_PATH,
        help = 'Specify the output directory.(default: %(default)s)')
    parser.add_argument(
        '-r', '--ramdump_image',
        default = '/dev/block/platform/msm_sdcc.1/by-name/ramdump',
        help = 'Specify the ramdump image.(default: %(default)s)')
    parser.add_argument(
        '-m', '--img_mount',
        default = '/data/ramdump',
        help = 'Specify the directory for ramdump image mount on.(default: %(default)s)')
    parser.add_argument(
        '-b', '--build_number',
        help = 'Specify the build number of the device. \
                Leave this empty means get the build number from the device.')

    args = parser.parse_args()

    global ADBPATH, OUTPATH, RDIMG, IMGMNT, BDNUM
    OUTPATH = args.out_path
    RDIMG = args.ramdump_image
    ADBPATH = args.adb_path
    IMGMNT = args.img_mount
    BDNUM = args.build_number

def rm_dir(src):
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            rm_dir(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass

def adb_shell(cmd):
    adb_shell_cmd = "%s shell %s" % (ADBPATH, cmd)
    print adb_shell_cmd
    cmd_rst = os.popen(adb_shell_cmd).readlines()
    return cmd_rst

if __name__ == '__main__':
    init()

    if os.path.isdir(TMP_PATH):
        rm_dir(TMP_PATH)
    os.mkdir(TMP_PATH)

    os.system("%s root" % (ADBPATH))
    time.sleep(1)
    os.system("%s remount" % (ADBPATH))

    adb_shell("umount %s" % (IMGMNT))
    adb_shell("rm -rf %s" % (IMGMNT))
    adb_shell("mkdir %s" % (IMGMNT))
    adb_shell("mount -t vfat %s %s" % (RDIMG, IMGMNT))
    os.system("%s pull %s %s" % (ADBPATH, IMGMNT, TMP_PATH))
    adb_shell("umount %s" % (IMGMNT))
    adb_shell("rm -rf %s" % (IMGMNT))

    BDNUM = BDNUM if   BDNUM \
                  else adb_shell("getprop %s" % (BN_PROP))[0].strip('\r\n')
    nowdate = datetime.datetime.now().strftime('%Y%m%d')
    tarname = "ramdump_%s_%s.tar.gz" % (BDNUM, nowdate)

    tar = tarfile.open(os.path.join(OUTPATH, tarname),'w:gz')
    for r, d, files in os.walk(TMP_PATH):
        for f in files:
            print os.path.join(r[len(WORK_PATH) + 1:],f)
            tar.add(os.path.join(r[len(WORK_PATH) + 1:],f))
    tar.close()

    rm_dir(TMP_PATH)
