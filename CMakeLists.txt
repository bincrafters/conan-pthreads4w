cmake_minimum_required(VERSION 3.5.0)

project(pthreads4w)

#
# Project options.
#

option(PTHREADS_BUILD_STATIC "Build static library" ON)
option(PTHREADS_EXCEPTION_SCHEME "Exception handling scheme (CPP/SEH/<none>)" "")

#
# Conan initialization.
#

include(conanbuildinfo.cmake)
conan_basic_setup()

if (MSVC AND CONAN_LINK_RUNTIME)
  set(flags
    CMAKE_C_FLAGS_DEBUG
    CMAKE_C_FLAGS_MINSIZEREL
    CMAKE_C_FLAGS_RELEASE
    CMAKE_C_FLAGS_RELWITHDEBINFO
    CMAKE_CXX_FLAGS_DEBUG
    CMAKE_CXX_FLAGS_MINSIZEREL
    CMAKE_CXX_FLAGS_RELEASE
    CMAKE_CXX_FLAGS_RELWITHDEBINFO)
  foreach(flag ${flags})
    if(${flag} MATCHES "/MD")
      string(REPLACE "/MDd " "${CONAN_LINK_RUNTIME} " ${flag} "${${flag}}")
      string(REPLACE "/MD " "${CONAN_LINK_RUNTIME} " ${flag} "${${flag}}")
    endif()
  endforeach()
endif()

#
# Source files.
#

set(PUBLIC_HEADERS
	sources/pthread.h
	sources/sched.h
	sources/semaphore.h)

set(PRIVATE_HEADERS
	sources/config.h
	sources/implement.h
	sources/need_errno.h)

set(SOURCES
	sources/attr.c
	sources/barrier.c
	sources/cancel.c
	sources/cleanup.c
	sources/condvar.c
	sources/create.c
	sources/autostatic.c
	sources/errno.c
	sources/exit.c
	sources/fork.c
	sources/global.c
	sources/misc.c
	sources/mutex.c
	sources/nonportable.c
	sources/private.c
	sources/rwlock.c
	sources/sched.c
	sources/semaphore.c
	sources/signal.c
	sources/spin.c
	sources/sync.c
	sources/tsd.c)

set(RESOURCES
	sources/version.rc)

if (NOT PTHREADS_BUILD_STATIC)
	list(APPEND SOURCES
		sources/dll.c)
endif()

#
# Target.
#

if (PTHREADS_BUILD_STATIC)
	add_library(${PROJECT_NAME} STATIC
		${SOURCES}
		${PUBLIC_HEADERS}
		${PRIVATE_HEADERS})
else()
	add_library(${PROJECT_NAME} SHARED
		${SOURCES}
		${PUBLIC_HEADERS}
		${PRIVATE_HEADERS}
		${RESOURCES})
endif()

set_target_properties(${PROJECT_NAME}
	PROPERTIES PUBLIC_HEADER "${PUBLIC_HEADERS}")

target_include_directories(${PROJECT_NAME}
	PRIVATE
		${CMAKE_CURRENT_SOURCE_DIR}/sources)

if (MSVC)
	# Use link time code generation in the Release builds. 
	set_target_properties(${PROJECT_NAME} PROPERTIES STATIC_LIBRARY_FLAGS_RELEASE "/LTCG")
endif()

#
# Compiler options.
#

if (MSVC)
	target_compile_definitions(${PROJECT_NAME}
		PRIVATE
			-DHAVE_PTW32_CONFIG_H)

	if (PTHREADS_EXCEPTION_SCHEME STREQUAL "CPP")
		target_compile_definitions(${PROJECT_NAME}
			PRIVATE
				-D__CLEANUP_CXX)
		set_source_files_properties(${SOURCES}
			PROPERTIES LANGUAGE CXX)
	elseif (PTHREADS_EXCEPTION_SCHEME STREQUAL "SEH")
		target_compile_definitions(${PROJECT_NAME}
			PRIVATE
				-D__CLEANUP_SEH)
	endif()

	if (PTHREADS_BUILD_STATIC)
		target_compile_definitions(${PROJECT_NAME}
			PUBLIC
				-DPTW32_STATIC_LIB)
	else()
		target_compile_definitions(${PROJECT_NAME}
		PRIVATE
			-DPTW32_RC_MSC)
	endif()

	if (CMAKE_SIZEOF_VOID_P EQUAL 8)
		target_compile_definitions(${PROJECT_NAME}
			PRIVATE
				-DPTW32_ARCH="x64")
	else()
		target_compile_definitions(${PROJECT_NAME}
			PRIVATE
				-DPTW32_ARCH="x86")
	endif()
endif()

#
# Installation.
#

install(TARGETS ${PROJECT_NAME}
	RUNTIME DESTINATION bin COMPONENT runtime
	LIBRARY DESTINATION lib COMPONENT dev
	ARCHIVE DESTINATION lib COMPONENT dev
	PUBLIC_HEADER DESTINATION include COMPONENT dev)
