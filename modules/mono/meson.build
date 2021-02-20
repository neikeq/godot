
subdir('build_scripts')

_module_mono_srcs = files()
_module_mono_cpp_args = []

################################################################################
# General sources
################################################################################

_module_mono_srcs += files([
    'class_db_api_json.cpp',
    'csharp_script.cpp',
    'godotsharp_dirs.cpp',
    'managed_callable.cpp',
    'mono_gc_handle.cpp',
    'register_types.cpp',
    'signal_awaiter_utils.cpp',
    'mono_gd/gd_mono_assembly.cpp',
    'mono_gd/gd_mono_cache.cpp',
    'mono_gd/gd_mono_class.cpp',
    'mono_gd/gd_mono_field.cpp',
    'mono_gd/gd_mono_internals.cpp',
    'mono_gd/gd_mono_log.cpp',
    'mono_gd/gd_mono_marshal.cpp',
    'mono_gd/gd_mono_method.cpp',
    'mono_gd/gd_mono_property.cpp',
    'mono_gd/gd_mono_utils.cpp',
    'mono_gd/gd_mono_wasm_m2n.cpp',
    'mono_gd/gd_mono.cpp',
    'mono_gd/managed_type.cpp',
    'utils/mono_reg_utils.cpp',
    'utils/osx_utils.cpp',
    'utils/path_utils.cpp',
    'utils/string_utils.cpp',
    'glue/base_object_glue.cpp',
    'glue/collections_glue.cpp',
    'glue/gd_glue.cpp',
    'glue/nodepath_glue.cpp',
    'glue/rid_glue.cpp',
    'glue/scene_tree_glue.cpp',
    'glue/string_glue.cpp',
    'glue/string_name_glue.cpp',
])

################################################################################
# Platform-specific sources
################################################################################

if PLATFORM == 'android'
    _module_mono_srcs += files([
        'mono_gd/support/android_support.cpp',
    ])
elif PLATFORM in ['osx', 'iphone']
    _module_mono_srcs += files([
        'mono_gd/support/ios_support.mm',
    ])
endif

################################################################################
# Tools sources
################################################################################

if get_option('tools')
    _module_mono_srcs += files([
        'editor/bindings_generator.cpp',
        'editor/code_completion.cpp',
        'editor/editor_internal_calls.cpp',
        'editor/godotsharp_export.cpp',
        'editor/script_class_parser.cpp',
    ])
endif

################################################################################
# Conditionally define GD_MONO_HOT_RELOAD
################################################################################

if get_option('tools') or IS_DEBUG_BUILD
    _module_mono_cpp_args += ['-DGD_MONO_HOT_RELOAD']
endif

################################################################################
# Variables
################################################################################

fs = import('fs')

_desktop_platforms = ['windows', 'osx', 'linuxbsd', 'server', 'uwp', 'haiku']
_unix_like_platforms = ['osx', 'linuxbsd', 'server', 'android', 'haiku', 'iphone']

_module_tools_unsupported_platforms = ['android', 'javascript', 'iphone']

################################################################################
# Find Mono
################################################################################

mono_prefix = get_option('mono_prefix')

if mono_prefix != ''
    mono_bin_dir = mono_prefix / 'bin'
    mono_etc_dir = mono_prefix / 'etc'
    mono_include_dir = mono_prefix / 'include/mono-2.0'
    mono_lib_dir = mono_prefix / 'lib'

    if not fs.is_dir(mono_etc_dir / 'mono')
        # Support specifying the '/usr' mono prefix manually.
        if fs.is_dir(mono_prefix / '../etc/mono')
            mono_etc_dir = mono_prefix / '../etc'
        elif fs.is_dir(mono_prefix / 'local/etc/mono')
            mono_etc_dir = mono_prefix / 'local/etc'
        else
            error('Cannot find \'etc\' directory for the specified mono prefix.')
        endif
    endif
endif

# Auto-detect Mono location
if mono_prefix == ''
    message('The \'mono_prefix\' Meson option was not specified. Attempting to auto-detect Mono\'s location...')

    if PLATFORM == 'windows'
        if build_machine.system() == 'windows'
            mono_prefix = run_command(SCRIPT_FIND_MONO_IN_WINREG, host_machine.cpu_family()).stdout().strip()
            if mono_prefix == ''
                error('Could not find Mono in the Windows Registry.')
            endif

            mono_bin_dir = mono_prefix / 'bin'
            mono_etc_dir = mono_prefix / 'etc'
            mono_include_dir = mono_prefix / 'include/mono-2.0'
            mono_lib_dir = mono_prefix / 'lib'

            message('Found Mono prefix in the Windows Registry: ' + mono_prefix)
        else
            error('The \'mono_prefix\' Meson option was not specified.')
        endif
    else
        mono_pkgconfig_dep = dependency('mono-2', method: 'pkg-config', required: false)
        if not mono_pkgconfig_dep.found()
            error('Could not find Mono via pkg-config.')
        endif

        mono_prefix = zdep.get_variable(pkgconfig: 'prefix', '')
        if mono_prefix == ''
            error('Could not find pkg-config \'prefix\' variable.')
        endif

        mono_pkgconfig_sysconfdir = zdep.get_variable(pkgconfig: 'sysconfdir', '')
        mono_pkgconfig_includedir = zdep.get_variable(pkgconfig: 'includedir', '')
        mono_pkgconfig_libdir = zdep.get_variable(pkgconfig: 'libdir', '')

        mono_bin_dir = mono_prefix / 'bin'
        mono_etc_dir = mono_pkgconfig_sysconfdir != '' ? mono_pkgconfig_sysconfdir : mono_prefix / 'etc'
        mono_include_dir = mono_pkgconfig_includedir != '' ? mono_pkgconfig_includedir : mono_prefix / 'include'
        mono_lib_dir = mono_pkgconfig_libdir != '' ? mono_pkgconfig_libdir : mono_prefix / 'lib'

        message('Found Mono prefix via pkg-config: ' + mono_prefix)
    endif
endif

################################################################################
# Find Mono BCL
################################################################################

mono_bcl = get_option('mono_bcl')
if mono_bcl == ''
    mono_bcl = mono_lib_dir / 'mono/4.5'
endif

################################################################################
# Find MSBuild or dotnet CLI
################################################################################

dotnet_cli = ''
msbuild_standalone = ''
msbuild_mono = ''

msbuild_tool_args = ['--mono-bin-dir', mono_bin_dir]

_find_msbuild_res = run_command(SCRIPT_FIND_MSBUILD, 'dotnet_cli')
if _find_msbuild_res.returncode() == 0
    dotnet_cli = _find_msbuild_res.stdout().strip()
    msbuild_tool_args += ['--tool-dotnet-cli', dotnet_cli]
endif

_find_msbuild_res = run_command(SCRIPT_FIND_MSBUILD, 'msbuild_standalone')
if _find_msbuild_res.returncode() == 0
    msbuild_standalone = _find_msbuild_res.stdout().strip()
    msbuild_tool_args += ['--tool-msbuild-standalone', msbuild_standalone]
endif

_find_msbuild_res = run_command(SCRIPT_FIND_MSBUILD, 'msbuild_mono', '--mono-prefix', mono_prefix)
if _find_msbuild_res.returncode() == 0
    msbuild_mono = _find_msbuild_res.stdout().strip()
    msbuild_tool_args += ['--tool-msbuild-mono', msbuild_mono]
endif

if dotnet_cli == '' and msbuild_standalone == '' and msbuild_mono == ''
    error('One of these tools is required but none could be found: dotnet CLI, standalone MSBuild, Mono\'s MSBuild.')
endif

################################################################################
# Generate C# glue version header
################################################################################

if get_option('tools')
    custom_target('cs_glue_version',
        output: ['cs_glue_version.gen.h'],
        input: 'glue/GodotSharp/GodotSharp.sln',
        depfile: 'cs_glue_version.depfile',
        command: [SCRIPT_CS_GLUE_VERSION] + msbuild_tool_args +
            ['--stamp', '@OUTPUT@', '--depfile', '@DEPFILE@', '--',
            '@INPUT@', '/p:ExcludeGeneratedSources=true'],
        build_by_default: true)
endif

################################################################################
# Conditionally define MONO_GLUE_ENABLED and ensure glue is generated
################################################################################

glue_gen_exists = fs.is_file('glue/mono_glue.gen.cpp')

if get_option('mono_glue')
    _module_mono_cpp_args += ['-DMONO_GLUE_ENABLED']

    if not glue_gen_exists
        error('Mono glue sources not found. Did you forget to run \'--generate-mono-glue\'?')
    endif
endif

if glue_gen_exists
    _module_mono_srcs += files('glue/mono_glue.gen.cpp')
endif

################################################################################
# TODO: Can this be removed now that we migrated to GitHub Actions? Or maybe Travis CI already updated Mono?
# Travis CI may have a Mono version lower than 5.12
# Disable use of Mono pending exceptions API for Travis builds
################################################################################

travis = run_command(SCRIPT_PRINT_ENV_VAR, 'TRAVIS').stdout().strip()
if travis == 'true'
    _module_mono_cpp_args += ['-DNO_PENDING_EXCEPTIONS']
endif

################################################################################
# Configure Mono
################################################################################

default_mono_static = PLATFORM in ['iphone', 'javascript']
default_mono_bundles_zlib = PLATFORM in ['javascript']

is_android = PLATFORM == 'android'
is_javascript = PLATFORM == 'javascript'
is_ios = PLATFORM == 'iphone'
is_ios_sim = is_ios and host_machine.cpu_family() in ['x86', 'x86_64']

mono_static = get_option('mono_static')
mono_static = mono_static == 'auto' ? default_mono_static : mono_static != 'false'

# TODO: Implement mono_bundles_zlib (how to disable builtin_zlib in Meson)
mono_bundles_zlib = get_option('mono_bundles_zlib')
mono_bundles_zlib = mono_bundles_zlib == 'auto' ? default_mono_bundles_zlib : mono_bundles_zlib != 'false'

# TODO:
# if is_android and not env["android_arch"] in android_arch_dirs:
#     raise RuntimeError("This module does not support the specified 'android_arch': " + env["android_arch"])

if get_option('tools') and PLATFORM in _module_tools_unsupported_platforms
    # TODO:
    # Android: We have to add the data directory to the apk, concretely the Api and Tools folders.
    error('This module does not currently support building for this platform with tools enabled')
endif

if is_android and mono_static
    # FIXME: When static linking and doing something that requires libmono-native, we get a dlopen error as 'libmono-native'
    # seems to depend on 'libmonosgen-2.0'. Could be fixed by re-directing to '__Internal' with a dllmap or in the dlopen hook.
    error('Statically linking Mono is not currently supported for this platform')
endif

if not mono_static and (is_javascript or is_ios)
    error('Dynamically linking Mono is not currently supported for this platform')
endif

# Although we don't support building with tools for any platform where we currently use static AOT,
# if these are supported in the future, we won't be using static AOT for them as that would be
# too restrictive for the editor. These builds would probably be made to only use the interpreter.
mono_aot_static = (is_ios and not is_ios_sim) and not get_option('tools')

# Static AOT is only supported on the root domain
mono_single_appdomain = mono_aot_static

if mono_single_appdomain
    _module_mono_cpp_args += ['-DGD_MONO_SINGLE_APPDOMAIN']
endif

if (get_option('tools') or IS_DEBUG_BUILD) and not mono_single_appdomain
    _module_mono_cpp_args += ['-DGD_MONO_HOT_RELOAD']
endif

_cpp = meson.get_compiler('cpp')

if PLATFORM == 'windows'
    is_msvc = meson.get_compiler('cpp').get_id() == 'msvc'

    if mono_static
        # Static Linking

        if is_msvc
            _mono_lib_dep = _cpp.find_library('mono-static-sgen', # libmono-static-sgen.lib
                    dirs: mono_lib_dir, static: true, required: false)
        else
            # MinGW supports both '.a' and '.lib'
            _mono_lib_dep = _cpp.find_library('monosgen-2.0', # libmonosgen-2.0.a
                    dirs: mono_lib_dir, static: true, required: false)

            if not _mono_lib_dep.found()
                # TODO: does linking this one work with MinGW?
                _mono_lib_dep = _cpp.find_library('mono-static-sgen', # libmono-static-sgen.lib
                        dirs: mono_lib_dir, static: true, required: false)
            endif
        endif

        if not _mono_lib_dep.found()
            error('Could not find static mono library in: ' + mono_lib_dir)
        endif

        if is_msvc
            _mono_other_lib_deps = [
                _cpp.find_library('Mincore', static: true, required: true),
                _cpp.find_library('msvcrt', static: true, required: true),
                _cpp.find_library('LIBCMT', static: true, required: true),
                _cpp.find_library('Psapi', static: true, required: true)
            ]
        else
            _mono_other_lib_deps = [
                _cpp.find_library('psapi', required: true),
                _cpp.find_library('version', required: true)
            ]
        endif

        link_whole = not is_msvc

        if link_whole
            _mono_dep = declare_dependency(link_whole: _mono_lib_dep)
        endif

        _mono_dep = declare_dependency(
            dependencies: [_mono_dep] + _mono_other_lib_deps
        )
    else
        # Dynamic Linking

        # dll file has same base name as lib file

        if is_msvc
            _mono_lib_dep = _cpp.find_library('mono-2.0-sgen', # mono-2.0-sgen.lib
                    dirs: mono_lib_dir, static: true, required: false)
            mono_dll_file_name = 'mono-2.0-sgen.dll'
        else
            # MinGW supports both '.a' and '.lib'
            _mono_lib_dep = _cpp.find_library('monosgen-2.0', # libmonosgen-2.0.a
                    dirs: mono_lib_dir, static: true, required: false)
            mono_dll_file_name = 'libmonosgen-2.0.dll'

            if not _mono_lib_dep.found()
                _mono_lib_dep = _cpp.find_library('mono-2.0-sgen', # mono-2.0-sgen.lib
                        dirs: mono_lib_dir, static: true, required: false)
                mono_dll_file_name = 'mono-2.0-sgen.dll'
            endif
        endif

        if not _mono_lib_dep.found()
            error('Could not find mono library in: ' + mono_lib_dir)
        endif

        _mono_dep = declare_dependency(
            dependencies: _mono_lib_dep
        )

        mono_dll_file_path = mono_bin_dir / mono_dll_file_name

        if not fs.is_file(mono_dll_file_path)
            error('Could not find mono dll in: ' + mono_bin_dir)
        endif

        custom_target(mono_dll_file_name,
            input: mono_dll_file_path,
            output: mono_dll_file_name,
            command: [SCRIPT_COPY_FILE, '@INPUT@', '@OUTPUT@'],
            install: true,
            install_dir: '@OUTDIR@',
            build_by_default: true)
    endif
else
    is_apple = PLATFORM in ['osx', 'iphone']
    is_macos = is_apple and not is_ios

    sharedlib_ext = is_apple ? '.dylib' : '.so'

    mono_so_file_name = ''

    if is_ios and not is_ios_sim
        _module_mono_cpp_args += ['-DIOS_DEVICE']
    endif

    _mono_lib_dep = _cpp.find_library('monosgen-2.0', # libmonosgen-2.0.a
            dirs: mono_lib_dir, static: mono_static, required: false)

    if not _mono_lib_dep.found()
        error('Could not find mono library in: ' + mono_lib_dir)
    endif

    _module_mono_cpp_args += ['-D_REENTRANT']

    if is_macos
        _mono_other_lib_deps = [
            _cpp.find_library('iconv', required: true),
            _cpp.find_library('pthread', required: true)
        ]
    elif is_android
        _mono_other_lib_deps = [] # Nothing
    elif is_ios
        _mono_other_lib_deps = [] # Nothing, linking is delegated to the exported Xcode project
    elif is_javascript
        _mono_other_lib_deps = [
            _cpp.find_library('m', required: true),
            _cpp.find_library('rt', required: true),
            _cpp.find_library('dl', required: true),
            _cpp.find_library('pthread', required: true)
        ]
    else
        _mono_other_lib_deps = [
            _cpp.find_library('m', required: true),
            _cpp.find_library('rt', required: true),
            _cpp.find_library('dl', required: true),
            _cpp.find_library('pthread', required: true)
        ]
    endif

    if mono_static
        _mono_dep_link_flags = []

        if not is_javascript
            _mono_dep_link_flags += '-rdynamic'
        endif

        # link_whole doesn't work with ExternalLibrary (find_library) because of reasons, so we need to do this manually...
        mono_lib_file_path = mono_lib_dir / 'libmonosgen-2.0.a'
        if is_apple
            if is_macos
                _mono_dep_link_flags += ['-Wl,-force_load,' + mono_lib_file_path]
            endif
        else
            _mono_dep_link_flags += ['-Wl,-whole-archive', mono_lib_file_path, '-Wl,-no-whole-archive']
        endif

        if is_apple
            if is_ios
                _mono_ios_arch = host_machine.cpu_family()

                # TODO: Fix old code that depends on this that's using the old arm64 naming instead of aarch64.
                assert(_mono_ios_arch in ['x86', 'x86_64', 'arm', 'aarch64'])

                _mono_libs_to_cp = []

                # Copy Mono libraries to the output folder. These are meant to be bundled with
                # the export templates and added to the Xcode project when exporting a game.
                _mono_libs_to_cp += 'libmonosgen-2.0.a'
                _mono_libs_to_cp += 'libmono-native'
                _mono_libs_to_cp += 'libmono-profiler-log'

                if not is_ios_sim
                    _mono_libs_to_cp += 'libmono-ee-interp'
                    _mono_libs_to_cp += 'libmono-icall-table'
                    _mono_libs_to_cp += 'libmono-ilgen'
                endif

                foreach mono_lib_to_cp : _mono_libs_to_cp
                    custom_target(mono_lib_to_cp,
                        input: mono_lib_dir / mono_lib_to_cp + '.a',
                        # FIXME: copies to builddir/modules/mono/ ...
                        output: mono_lib_to_cp + '.a.stamp',
                        command: [SCRIPT_COPY_FILE, '@INPUT@',
                                meson.project_build_root() / mono_lib_to_cp + '.iphone.' + _mono_ios_arch + '.a',
                                '--stamp', '@OUTPUT@'],
                        install: true,
                        install_dir: '@OUTDIR@',
                        build_by_default: true)
                endforeach
            endif
        else
            assert(PLATFORM in _desktop_platforms or is_android or is_javascript)
        endif

        if is_javascript
            _mono_other_lib_deps += [
                _cpp.find_library('mono-icall-table', dirs: mono_lib_dir, static: true, required: true),
                _cpp.find_library('mono-native', dirs: mono_lib_dir, static: true, required: true),
                _cpp.find_library('mono-ilgen', dirs: mono_lib_dir, static: true, required: true),
                _cpp.find_library('mono-ee-interp', dirs: mono_lib_dir, static: true, required: true)
            ]

            wasm_src_dir = mono_prefix / 'src'
            if not fs.is_dir(wasm_src_dir)
                error('Could not find mono wasm src directory')
            endif

            _mono_dep_link_flags += [
                '--js-library', wasm_src_dir / 'library_mono.js',
                '--js-library', wasm_src_dir / 'binding_support.js',
                '--js-library', wasm_src_dir / 'dotnet_support.js',
            ]

            _mono_dep = declare_dependency(
                include_directories: include_directories(mono_include_dir),
                #link_whole: _mono_lib_dep,
                dependencies: _mono_other_lib_deps,
                link_args: _mono_dep_link_flags,
                # Ideally this should be defined only for 'driver.c', but I can't fight scons for another 2 hours (TODO: is this comment still true with Meson?)
                compile_args: ['-DCORE_BINDINGS'],
                sources: [
                    wasm_src_dir / 'driver.c',
                    wasm_src_dir / 'zlib-helper.c',
                    wasm_src_dir / 'corebindings.c'
                ]
            )
        else
            _mono_dep = declare_dependency(
                #link_whole: _mono_lib_dep,
                dependencies: _mono_other_lib_deps,
                link_args: _mono_dep_link_flags
            )
        endif
    else
        _mono_dep = declare_dependency(
            dependencies: [_mono_lib_dep] + _mono_other_lib_deps
        )
    endif

    if not mono_static
        mono_so_file_name = 'libmonosgen-2.0' + sharedlib_ext

        if not fs.is_file(mono_lib_dir / mono_so_file_name)
            error('Could not find mono shared library in: ' + mono_lib_dir)
        endif
    endif

    if not mono_static
        if is_android
        mono_so_output = meson.project_build_root() / mono_so_file_name
            # TODO
            # android_output_dir = Dir('#platform/android/java/lib/libs').abspath /
            #         'release' if env['target'] == 'release' else 'debug' /
            #         android_arch_dirs[env['android_arch']]
            # mono_so_output = android_output_dir / mono_so_file_name
        endif

        custom_target(mono_so_file_name,
            input: mono_lib_dir / mono_so_file_name,
            # FIXME: copies to builddir/modules/mono/ ...
            output: mono_so_file_name + '.stamp',
            command: [SCRIPT_COPY_FILE, '@INPUT@', mono_so_output, '--stamp', '@OUTPUT@'],
            install: true,
            install_dir: '@OUTDIR@',
            build_by_default: true)
    endif
endif

_mono_shared_libs_output_dir = ''
_mono_etc_files_output_dir = ''
_mono_bcl_output_dir = ''

if not get_option('tools')
    if PLATFORM in _desktop_platforms
        # Only desktop export templates have a data directory
        assert(PLATFORM in _desktop_platforms)

        # TODO: Fix old code that depends on this that's using bits (32/64) instead of arch.
        # TODO: Fix target? Where is release_debug? How to check this in Meson?
        _mono_template_dir_name = 'data.mono.' + PLATFORM + '.' + host_machine.cpu_family() + '.' + (IS_DEBUG_BUILD ? 'debug' : 'release')

        _target_mono_prefix = meson.project_build_root() / _mono_template_dir_name / 'Mono'
        _mono_shared_libs_output_dir = _target_mono_prefix / (PLATFORM == 'windows' ? 'bin' : 'lib')
        _mono_etc_files_output_dir = _target_mono_prefix / 'etc'
    elif is_android
        # TODO:
        # # Compress Android Mono Config
        # from . import make_android_mono_config

        # module_dir = os.getcwd()
        # config_file_path = os.path.join(module_dir, "build_scripts", "mono_android_config.xml")
        # make_android_mono_config.generate_compressed_config(config_file_path, "mono_gd/")

        # target_mono_lib_dir = get_android_out_dir(env)
        # # Copy the required shared libraries
        # copy_mono_shared_libs(env, mono_prefix, None)
    elif is_javascript or is_ios
        # No data directory for these platform
    endif
endif

if get_option('copy_mono_root')
    if get_option('tools')
        _target_mono_prefix = meson.project_build_root() / 'GodotSharp/Mono'
        _mono_shared_libs_output_dir = _target_mono_prefix / (PLATFORM == 'windows' ? 'bin' : 'lib')
        _mono_etc_files_output_dir = _target_mono_prefix / 'etc'
        _mono_bcl_output_dir = _target_mono_prefix / 'lib/mono/4.5'
    else
        error('The Meson option \'copy_mono_root\' can only be enabled together with \'tools\'.')
    endif
endif

################################################################################
# Copy Mono Etc Files
################################################################################

if _mono_etc_files_output_dir != ''
    _mono_etc_config_output = _mono_etc_files_output_dir / 'mono/config'
    custom_target('mono_etc_mono_config',
        input: mono_etc_dir / 'mono/config',
        # FIXME: copies to builddir/modules/mono/ ...
        output: 'mono_etc_mono_config.stamp',
        command: [SCRIPT_COPY_FILE, '@INPUT@', _mono_etc_config_output, '--stamp', '@OUTPUT@'],
        install: true,
        install_dir: '@OUTDIR@',
        build_by_default: true)
endif

################################################################################
# Copy Mono Shared Libraries
################################################################################

if _mono_shared_libs_output_dir != ''
    if PLATFORM == 'windows'
        _mono_output_bin_dir = _mono_shared_libs_output_dir

        if fs.is_file(mono_bin_dir / 'libMonoPosixHelper.dll')
            # Naming for Mono built with MinGW
            mono_posix_helper_file = 'libMonoPosixHelper.dll'
        else
            mono_posix_helper_file = 'MonoPosixHelper.dll'
        endif

        custom_target('MonoPosixHelper',
            input: mono_bin_dir / mono_posix_helper_file,
            # FIXME: copies to builddir/modules/mono/ ...
            output: 'MonoPosixHelper.dll.stamp',
            command: [SCRIPT_COPY_FILE, '@INPUT@', _mono_shared_libs_output_dir / 'MonoPosixHelper.dll', '--stamp', '@OUTPUT@'],
            install: true,
            install_dir: '@OUTDIR@',
            build_by_default: true)

        # For newer versions
        btls_dll_path = mono_bin_dir / 'libmono-btls-shared.dll'
        if fs.is_file(btls_dll_path)
            custom_target('libmono-btls-shared',
                input: btls_dll_path,
                # FIXME: copies to builddir/modules/mono/ ...
                output: 'libmono-btls-shared.dll.stamp',
                command: [SCRIPT_COPY_FILE, '@INPUT@', _mono_shared_libs_output_dir / 'libmono-btls-shared.dll', '--stamp', '@OUTPUT@'],
                install: true,
                install_dir: '@OUTDIR@',
                build_by_default: true)
        endif
    else
        if PLATFORM == 'osx'
            lib_file_names = ['libmono-btls-shared.dylib', 'libmono-native-compat.dylib', 'libMonoPosixHelper.dylib']
        elif PLATFORM in _unix_like_platforms
            lib_file_names = [
                'libmono-btls-shared.so',
                'libmono-ee-interp.so',
                'libmono-native.so',
                'libMonoPosixHelper.so',
                'libmono-profiler-aot.so',
                'libmono-profiler-coverage.so',
                'libmono-profiler-log.so',
                'libMonoSupportW.so',
            ]
        endif

        foreach lib_file_name : lib_file_names
            if fs.is_file(mono_lib_dir / lib_file_name)
                custom_target(fs.replace_suffix(lib_file_name, ''),
                    input: mono_lib_dir / lib_file_name,
                    # FIXME: copies to builddir/modules/mono/ ...
                    output: lib_file_name + '.stamp',
                    command: [SCRIPT_COPY_FILE, '@INPUT@', _mono_shared_libs_output_dir / lib_file_name, '--stamp', '@OUTPUT@'],
                    install: true,
                    install_dir: '@OUTDIR@',
                    build_by_default: true)
            endif
        endforeach
    endif
endif

################################################################################
# Copy Mono BCL Assemblies
################################################################################

if _mono_bcl_output_dir != ''
    mono_bcl_facades_dir = mono_bcl / 'Facades'

    _mono_bcl_facades_output_dir = _mono_bcl_output_dir / 'Facades'

    _mono_bcl_assemblies = run_command(SCRIPT_LIST_DIR_ASSEMBLIES, mono_bcl) \
        .stdout().strip().split('\n')
    _mono_bcl_facade_assemblies = run_command(SCRIPT_LIST_DIR_ASSEMBLIES, mono_bcl_facades_dir) \
        .stdout().strip().split('\n')

    foreach assembly : _mono_bcl_assemblies
        custom_target(fs.replace_suffix(assembly, ''),
            input: mono_bcl / assembly,
            # FIXME: copies to builddir/modules/mono/ ...
            output: assembly + '.stamp',
            command: [SCRIPT_COPY_FILE, '@INPUT@', _mono_bcl_output_dir / assembly, '--stamp', '@OUTPUT@'],
            install: true,
            install_dir: '@OUTDIR@',
            build_by_default: true)
    endforeach
    foreach assembly : _mono_bcl_facade_assemblies
        custom_target(fs.replace_suffix(assembly, ''),
            input: mono_bcl_facades_dir / assembly,
            # FIXME: copies to builddir/modules/mono/ ...
            output: assembly + '.stamp',
            command: [SCRIPT_COPY_FILE, '@INPUT@', _mono_bcl_facades_output_dir / assembly, '--stamp', '@OUTPUT@'],
            install: true,
            install_dir: '@OUTDIR@',
            build_by_default: true)
    endforeach
endif

################################################################################
# Build MSBuild solutions: GodotSharp, GodotTools and Godot.NET.Sdk
################################################################################

if get_option('tools') and get_option('mono_glue') and get_option('build_cil')
    # GodotSharp target
    custom_target('sln_godotsharp_debug',
        # FIXME: https://github.com/mesonbuild/meson/issues/2320
        output: 'sln_godotsharp_debug.stamp',
        # output: [
        #     'GodotSharp/Api/Debug/GodotSharp.dll',
        #     'GodotSharp/Api/Debug/GodotSharp.pdb',
        #     'GodotSharp/Api/Debug/GodotSharp.xml',
        #     'GodotSharp/Api/Debug/GodotSharpEditor.dll',
        #     'GodotSharp/Api/Debug/GodotSharpEditor.pdb',
        #     'GodotSharp/Api/Debug/GodotSharpEditor.xml',
        # ],
        input: 'glue/GodotSharp/GodotSharp.sln',
        depfile: 'sln_godotsharp_debug.depfile',
        command: [SCRIPT_RUN_MSBUILD] + msbuild_tool_args +
            ['--depfile', '@DEPFILE@', '--stamp', '@OUTPUT@', '--targets', 'Build', '--',
            '@INPUT@', '/restore', '/p:Configuration=Debug', '/p:NoWarn=1591',
            '/p:MesonBuildDir=' + meson.project_build_root()],
        build_by_default: true)

    custom_target('sln_godotsharp_release',
        # FIXME: https://github.com/mesonbuild/meson/issues/2320
        output: 'sln_godotsharp_release.stamp',
        # output: [
        #     'GodotSharp/Api/Release/GodotSharp.dll',
        #     'GodotSharp/Api/Release/GodotSharp.pdb',
        #     'GodotSharp/Api/Release/GodotSharp.xml',
        #     'GodotSharp/Api/Release/GodotSharpEditor.dll',
        #     'GodotSharp/Api/Release/GodotSharpEditor.pdb',
        #     'GodotSharp/Api/Release/GodotSharpEditor.xml',
        # ],
        input: 'glue/GodotSharp/GodotSharp.sln',
        depfile: 'sln_godotsharp_release.depfile',
        command: [SCRIPT_RUN_MSBUILD] + msbuild_tool_args +
            ['--depfile', '@DEPFILE@', '--stamp', '@OUTPUT@', '--targets', 'Build', '--',
            '@INPUT@', '/restore', '/p:Configuration=Release', '/p:NoWarn=1591',
            '/p:MesonBuildDir=' + meson.project_build_root()],
        build_by_default: true)

    _godottools_output_names = [
        'GodotTools.BuildLogger.dll',
        'GodotTools.Core.dll',
        'GodotTools.dll',
        'GodotTools.IdeMessaging.dll',
        'GodotTools.ProjectEditor.dll',
        'GodotTools.Shared.dll',
        'Microsoft.Build.dll',
        'Microsoft.Build.Framework.dll',
        'Microsoft.VisualStudio.Setup.Configuration.Interop.dll',
        'MSBuild.exe',
        'Newtonsoft.Json.dll',
        'System.Buffers.dll',
        'System.Collections.Immutable.dll',
        'System.Memory.dll',
        'System.Numerics.Vectors.dll',
        'System.Runtime.CompilerServices.Unsafe.dll',
        'System.Threading.Tasks.Dataflow.dll',
    ]

    _godottools_output_names_debug = [
        'GodotTools.BuildLogger.pdb',
        'GodotTools.Core.pdb',
        'GodotTools.IdeMessaging.pdb',
        'GodotTools.pdb',
        'GodotTools.ProjectEditor.pdb',
        'GodotTools.Shared.pdb',
    ]

    if PLATFORM == 'windows'
        _godottools_output_names += [
            'EnvDTE.dll',
            'GodotTools.OpenVisualStudio.exe',
            'GodotTools.OpenVisualStudio.exe.config',
            'GodotTools.OpenVisualStudio.pdb',
            'stdole.dll',
        ]

        _godottools_output_names_debug += [
            'GodotTools.OpenVisualStudio.pdb',
        ]
    endif

    _sln_godottools_output = []

    foreach f : _godottools_output_names
        _sln_godottools_output += 'GodotSharp/Tools' / f
    endforeach

    if IS_DEBUG_BUILD
        foreach f : _godottools_output_names_debug
            _sln_godottools_output += 'GodotSharp/Tools' / f
        endforeach
    endif

    # GodotTools target
    custom_target('sln_godottools',
        # FIXME: https://github.com/mesonbuild/meson/issues/2320
        output: 'sln_godottools.stamp',
        # output: _sln_godottools_output,
        input: 'editor/GodotTools/GodotTools.sln',
        depfile: 'sln_godottools.depfile',
        command: [SCRIPT_RUN_MSBUILD] + msbuild_tool_args +
            ['--depfile', '@DEPFILE@', '--stamp', '@OUTPUT@', '--targets', 'Build', '--',
            '@INPUT@', '/restore', '/p:Configuration=' + (IS_DEBUG_BUILD ? 'Debug' : 'Release'),
            '/p:GodotPlatform=' + PLATFORM, '/p:MesonBuildDir=' + meson.project_build_root()],
        build_by_default: true)

    _godot_net_sdk_version_file = 'editor/Godot.NET.Sdk/Godot.NET.Sdk/Godot.NET.Sdk_PackageVersion.txt'
    _godot_net_sdk_version = run_command(SCRIPT_PRINT_FILE, _godot_net_sdk_version_file).stdout().strip()

    # Godot.NET.Sdk target
    custom_target('sln_godot_net_sdk',
        # FIXME: https://github.com/mesonbuild/meson/issues/2320
        output: 'sln_godot_net_sdk.stamp',
        # # FIXME: If the version changes, the target is rebuilt but 'output' is still named after the old version... What can be done about this?
        # output: ['GodotSharp/Tools/nupkgs/Godot.NET.Sdk.' + _godot_net_sdk_version + '.nupkg'],
        input: 'editor/Godot.NET.Sdk/Godot.NET.Sdk.sln',
        depfile: 'sln_godot_net_sdk.depfile',
        command: [SCRIPT_RUN_MSBUILD] + msbuild_tool_args +
            ['--depfile', '@DEPFILE@', '--stamp', '@OUTPUT@', '--targets', 'Build', '--',
            '@INPUT@', '/restore', '/p:Configuration=Release', '/p:GodotPlatform=' + PLATFORM,
            '/p:MesonBuildDir=' + meson.project_build_root()],
        build_by_default: true)
endif

################################################################################
# Declare Mono module library
################################################################################

lib_module_mono = library('module_mono', _module_mono_srcs,
    dependencies: [DEP_GODOT_ALL],
    cpp_args: _module_mono_cpp_args,
    include_directories: include_directories(mono_include_dir)
)

DEP_MODULE_MONO = declare_dependency(link_with: lib_module_mono, dependencies: _mono_dep)

MODULE_DEPENDENCIES += DEP_MODULE_MONO
