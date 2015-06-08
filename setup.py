# coding: utf-8
import setuptools

setuptools.setup(
    name='Rels',
    version='0.2.2',
    description='Library for describing data relations in python (Enums, "relational" tables)',
    long_description = open('README.rst').read(),
    url='https://github.com/Tiendil/rels',
    author='Aleksey Yeletsky <Tiendil>',
    author_email='a.eletsky@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',

        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',

        'Natural Language :: English',
        'Natural Language :: Russian'],
    keywords=['enums', 'data relations', 'relational tables'],
    packages=setuptools.find_packages(),
    include_package_data=True,
    test_suite = 'tests',
    )
