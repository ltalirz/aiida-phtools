# aiida-phtools

AiiDA plugin for persistence homology tools, used to analyze nanoporous materials.

# Installation

```shell
git clone https://github.com/ltalirz/aiida-phtools .
cd aiida-phtools
pip install -e .  # also installs aiida, if missing (but not postgres)
#pip install -e .[precommit,testing] # install extras for more features
verdi quicksetup  # better to set up a new profile
verdi calculation plugins  # should now show your calclulation plugins
```

# Usage

Here goes a complete example of how to submit a test calculation using this plugin.

# License

MIT

# Contact

leopold.talirz@gmail.com
