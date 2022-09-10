# For reference ~ https://github.com/pypa/sampleproject/blob/main/setup.py

import pathlib

from setuptools import setup, find_packages

# Cf. https://github.com/dave-shawley/setupext-janitor#installation
try:
   from setupext_janitor import janitor
   cleanCommand = janitor.CleanCommand
except ImportError:
   cleanCommand = None

cmd_classes = {}
if cleanCommand is not None:
   cmd_classes['clean'] = cleanCommand


here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='kvm-autoscaler',
    version='0.0.1',
    description='Autoscaling for KVM virtual machines over the libvirt API.',
    cmdclass=cmd_classes,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Emma Doyle',
    author_email='bjd2385.linux@gmail.com',
    keywords='kvm, virtualization, virtual machine, vm, autoscaler, autoscaling, libvirt',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.8, <4',
    url = 'https://github.com/bjd2385/autoscaler',
    install_requires=[],
    entry_points={
        "console_scripts": ["autoscaled = daemon.server:main"]
    },
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/bjd2385/autoscaler/issues',
        'Source': 'https://github.com/bjd2385/autoscaler'
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
