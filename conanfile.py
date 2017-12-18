#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class LibnameConan(ConanFile):
    name = "pthreads4w"
    version = "2.9.1"
    url = "https://github.com/bincrafters/conan-libname"
    description = "POSIX Threads for Windows"
    license = "https://github.com/someauthor/somelib/blob/master/LICENSES"
    exports_sources = ["CMakeLists.txt", "LICENSE.md", "pthread.h.diff", "ptw32_MCS_lock.c.diff"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
        "exception_scheme": ["CPP", "SEH", "default"]}
    default_options = "shared=False", \
        "exception_scheme=default"
    generators = "cmake"

    def source(self):
        snapshot_name = "pthreads4w-code-cc6ba2cc027526e1973e75121d92bb5495bc96ae"
        source_url = "https://sourceforge.net/code-snapshots/git/p/pt/pthreads4w/code.git"
        tools.get("{0}/{1}.zip".format(source_url, snapshot_name))
        extracted_dir = snapshot_name
        os.rename(extracted_dir, "sources")
        #Rename to "sources" is a convention to simplify later steps
        tools.patch(base_path="sources", patch_file="pthread.h.diff")
        tools.patch(base_path="sources", patch_file="ptw32_MCS_lock.c.diff")

    def build(self):
        cmake = CMake(self)

        if self.options.shared:
            cmake.definitions["PTHREADS_BUILD_STATIC"] = "OFF"
        else:
            cmake.definitions["PTHREADS_BUILD_STATIC"] = "ON"

        if self.options.exception_scheme == "CPP":
            cmake.definitions["PTHREADS_EXCEPTION_SCHEME"] = "CPP"
        elif self.options.exception_scheme == "SEH":
            cmake.definitions["PTHREADS_EXCEPTION_SCHEME"] = "SEH"

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        pass

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if not self.options.shared:
            self.cpp_info.defines = ["PTW32_STATIC_LIB"]
