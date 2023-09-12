# Mirror of hplip releases from Sourceforge

This repository mirrors the 
[hplip releases](https://sourceforge.net/projects/hplip/files/hplip/) on Sourceforge
in git format. The intention is to be able to review the code and the changes
between releases easily. 

**The owner of this repository is neither author nor maintainer of hplip**.

## Resources

* [hplip home page](https://developers.hp.com/hp-linux-imaging-and-printing)
* [hplip bug tracker on launchpad](https://launchpad.net/hplip).
  Please report hplip bugs there.
* [hplip sourceforge page](https://sourceforge.net/projects/hplip)

## License

The hplip code is released under different open source licenses. See
[COPYING](COPYING) for details. See individual source files for copyright holders.

## Building hplip

In general, building from this repository is not intended and not
recommended. If you want to build, please download the official tar balls.

If you want to build hplip from this repository, you will need to run the
script `git-helpers/recompress.sh` first. The reason is that compressed
content of the tar balls from sourceforge is uncompressed before adding
it to the repository. The `recompress.sh` script compresses these files
again to restore the build environment.
