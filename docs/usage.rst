=====
Usage
=====

Run from script
---------------

The fmu.config module is accessed through a script, which is ran like this::

  fmuconfig global_config.yml

The global config *shall* be placed at rXXX/share/config, where XXX is
the revision number.

File format and nested files
----------------------------

The config file itself is a YAML formatted file. It follows the standard
YAML spesification, with *one major exception*, and that is that
*file nesting* is allowed. This allows for placing various parts of
the CONFIG into separate subfiles.

What will be a good practice regarding this remains to see.

Some conventions
----------------

The examples section (next) should be studied in detail in order to
understand the format.

* YAML is a indent based file type; which means changing the indentation
  may change tha whole meaning of the file!

* The first level indentation is important. It can be

  - ``global``: For general settings
  - ``rms``: For RMS related settings
  - ``eclipse``: For Eclipse related settings

* Notice the difference beteen small letters and upprcase letters
  - The small letters are YAML keyword
  - Uppercase letters are "client" keywords or variables

* The dates format shall be `ISO 8601`_ complient, on the form ``YYYY-MM-DD``.
  For files that date will be usually be compressed to the ``YYYYMMDD`` form,
  which is still in accordance to the ISO standard.


Learn by example!
-----------------

Learn the format by studying the following examples.



.. _ISO 8601: https://en.wikipedia.org/wiki/ISO_8601
