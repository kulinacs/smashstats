# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='smashstats',
    version='0.1.0',

    description='Statistics on Super Smash Bros. Games',

    url='https://github.com/kulinacs/smashstats',

    author='Nicklaus McClendon',
    author_email='nicklaus@kulinacs.com',

    license='ISC',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python :: 3.7',
    ],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.png'],
    },

    keywords='smashbros',

    packages=find_packages(),

    install_requires=['opencv-python'],
)
