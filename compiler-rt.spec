%ifarch s390 s390x
# only limited set of libs available on s390(x) and the existing ones (stats, ubsan) don't provide debuginfo
%global debug_package %{nil}
%endif

#%%global rc_ver 3

%global crt_srcdir compiler-rt-%{version}%{?rc_ver:rc%{rc_ver}}.src

Name:		compiler-rt
Version:	7.0.1
Release:	2%{?rc_ver:.rc%{rc_ver}}%{?dist}
Summary:	LLVM "compiler-rt" runtime libraries

License:	NCSA or MIT
URL:		http://llvm.org
Source0:	http://%{?rc_ver:pre}releases.llvm.org/%{version}/%{?rc_ver:rc%{rc_ver}}/%{crt_srcdir}.tar.xz

Patch0: 0001-cmake-Don-t-prefer-python2.7.patch
Patch1: 0001-sanitizer-Remove-rsp-from-the-clobber-list-in-intern.patch

BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	cmake
BuildRequires:	python3
# We need python3-devel for pathfix.py.
BuildRequires:	python3-devel
BuildRequires:	llvm-devel = %{version}
BuildRequires:	llvm-static = %{version}

%description
The compiler-rt project is a part of the LLVM project. It provides
implementation of the low-level target-specific hooks required by
code generation, sanitizer runtimes and profiling library for code
instrumentation, and Blocks C language extension.

%prep
%autosetup -n %{crt_srcdir} -p1

pathfix.py -i %{__python3} -pn .

%build
mkdir -p _build
cd _build
%cmake .. \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DLLVM_CONFIG_PATH:FILEPATH=%{_bindir}/llvm-config-%{__isa_bits} \
	\
%if 0%{?__isa_bits} == 64
	-DLLVM_LIBDIR_SUFFIX=64 \
%else
	-DLLVM_LIBDIR_SUFFIX= \
%endif
	-DCOMPILER_RT_INCLUDE_TESTS:BOOL=OFF # could be on?

make %{?_smp_mflags}

%install
cd _build
make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib

%ifarch aarch64
%global aarch64_blacklists hwasan_blacklist.txt
%endif

for file in %{aarch64_blacklists} asan_blacklist.txt msan_blacklist.txt dfsan_blacklist.txt cfi_blacklist.txt dfsan_abilist.txt hwasan_blacklist.txt; do
	mv -v %{buildroot}%{_datadir}/${file} %{buildroot}%{_libdir}/clang/%{version}/ || :
done

# move sanitizer libs to better place
%global libclang_rt_installdir lib/linux
mv -v %{buildroot}%{_prefix}/%{libclang_rt_installdir}/libclang_rt* %{buildroot}%{_libdir}/clang/%{version}/lib
mkdir -p %{buildroot}%{_libdir}/clang/%{version}/lib/linux/
pushd %{buildroot}%{_libdir}/clang/%{version}/lib
for i in *.a *.syms *.so; do
	ln -s ../$i linux/$i
done

%check
cd _build
#make check-all

%files
%{_includedir}/*
%{_libdir}/clang/%{version}

%changelog
* Fri Jan 18 2019 sguelton@redhat.com - 7.0.1-2
- GCC-9 compatibility

* Mon Dec 17 2018 sguelton@redhat.com - 7.0.1-1
- 7.0.1 Release

* Tue Dec 04 2018 sguelton@redhat.com - 7.0.0-2
- Ensure rpmlint passes on specfile

* Mon Sep 24 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-1
- 7.0.0-1 Release

* Wed Sep 12 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.4.rc3
- 7.0.0-rc3 Release

* Fri Sep 07 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.3.rc1
- Use python3 for build scripts

* Thu Sep 06 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.2.rc1
- Drop BuildRequires: python2

* Tue Aug 14 2018 Tom Stellard <tstellar@redhat.com> - 7.0.0-0.1.rc1
- 7.0.0-rc1 Release

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Thu Jun 28 2018 Tom Stellard <tstellar@redhat.com> - 6.0.1-1
- 6.0.1 Release

* Mon Mar 19 2018 Iryna Shcherbina <ishcherb@redhat.com> - 6.0.0-2
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Thu Mar 08 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-1
- 6.0.0 Release

* Tue Feb 13 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.4.rc2
- 6.0.0-rc2 Release

* Tue Feb 13 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.3.rc1
- Fix build on AArch64

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 6.0.0-0.2.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 25 2018 Tom Stellard <tstellar@redhat.com> - 6.0.0-0.1.rc1
- 6.0.0-rc1 Release

* Wed Jan 17 2018 Tom Stellard <tstellar@redhat.com> - 5.0.1-2
- Build libFuzzer with gcc

* Wed Dec 20 2017 Tom Stellard <tstellar@redhat.com> - 5.0.1-1
- 5.0.1 Release

* Fri Oct 13 2017 Tom Stellard <tstellar@redhat.com> - 5.0.0-1
- 5.0.0 Release

* Mon Sep 25 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-6
- Fix AArch64 build with glibc 2.26

* Tue Sep 12 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-5
- Package libFuzzer

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.0.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jun 23 2017 Tom Stellard <tstelar@redhat.com> - 4.0.1-2
- Fix build with newer glibc

* Fri Jun 23 2017 Tom Stellard <tstellar@redhat.com> - 4.0.1-1
- 4.0.1 Release

* Tue Mar 14 2017 Tom Stellard <tstellar@redhat.com> - 4.0.0-1
- compiler-rt 4.0.0 Final Release

* Thu Mar 02 2017 Dave Airlie <airlied@redhat.com> - 3.9.1-1
- compiler-rt 3.9.1

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 3.9.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Nov 21 2016 Dan Horák <dan[at]danny.cz> - 3.9.0-3
- disable debuginfo on s390(x)

* Wed Nov 02 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-2
- build for new arches.

* Wed Oct 26 2016 Dave Airlie <airlied@redhat.com> - 3.9.0-1
- compiler-rt 3.9.0 final release

* Mon May  2 2016 Tom Callaway <spot@fedoraproject.org> 3.8.0-2
- make symlinks to where the linker thinks these libs are

* Thu Mar 10 2016 Dave Airlie <airlied@redhat.com> 3.8.0-1
- compiler-rt 3.8.0 final release

* Thu Mar 03 2016 Dave Airlie <airlied@redhat.com> 3.8.0-0.2
- compiler-rt 3.8.0rc3

* Thu Feb 18 2016 Dave Airlie <airlied@redhat.com> - 3.8.0-0.1
- compiler-rt 3.8.0rc2

* Fri Feb 05 2016 Dave Airlie <airlied@redhat.com> 3.7.1-3
- fix compiler-rt paths - from rwindz0@gmail.com - #1304605

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 3.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Oct 06 2015 Jan Vcelak <jvcelak@fedoraproject.org> 3.7.0-100
- initial version using cmake build system
