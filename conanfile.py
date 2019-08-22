#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools


class Pthreads4WConan(ConanFile):
    name = "pthreads4w"
    version = "2.9.1"
    url = "https://sourceforge.net/projects/pthreads4w/"
    source_url = "git://git.code.sf.net/p/pthreads4w/code"
    git_tag = "v-2-9-1-release"
    description = "POSIX Threads for Windows"
    license = "https://sourceforge.net/directory/license:lgpl/"
    exports_sources = ["CMakeLists.txt", "LICENSE.md", "pthread.h.diff", "ptw32_MCS_lock.c.diff"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False],
        "exception_scheme": ["CPP", "SEH", "default"]}
    default_options = {'shared': False, 'exception_scheme': 'default'}
    generators = "cmake"

    def source(self):
        self.run("git clone --depth=1 --branch={0} {1} sources"
            .format(self.git_tag, self.source_url))
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
