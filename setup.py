import setuptools
import pathlib

with open("README.md", "r") as fh:
    long_description = fh.read()

with open(pathlib.Path(__file__).parent / 'dj_nwb_adapter' / 'meta.py') as f:
    exec(f.read())

setuptools.setup(
    name=pkg_name,
    version=__version__,
    author="Thinh Nguyen",
    author_email="thinh@vathes.com",
    description="Unofficial DataJoint NWB type plugin.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ttngu207/djpyplugin_nwb",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=['setuptools_certificate'],
    install_requires=['datajoint', 'pynwb'],
    entry_points={
        'datajoint.plugins': 'attribute_adapter = {}'.format(pkg_name)
    },
)
