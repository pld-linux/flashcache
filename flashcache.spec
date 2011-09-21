#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace programs
%bcond_with	verbose		# verbose build (V=1)

%if %{without kernel}
%undefine	with_dist_kernel
%endif

%define		rel	0.1
Summary:	Flashcache - A Write Back Block Cache for Linux
Name:		flashcache
Version:	1.0
Release:	%{rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	https://github.com/facebook/flashcache/tarball/1.0#/%{name}-%{version}.tgz
# Source0-md5:	7b997160231bc67ce3751019ca7d7de0
URL:		https://github.com/facebook/flashcache/
%if %{with kernel}
%if %{with dist_kernel}
BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.18
BuildRequires:	kernel%{_alt_kernel}-source
%endif
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%{?with_userspace:BuildRequires:	perl-tools-pod}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Flashcache is a write back block cache Linux kernel module.

Flashcache was built primarily as a block cache for InnoDB but is
general purpose and can be used by other applications as well.

%package -n kernel%{_alt_kernel}-block-flashcache
Summary:	FlashCache is a general purpose writeback block cache for Linux
Release:	%{rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif

%description -n kernel%{_alt_kernel}-block-flashcache
Flashcache Linux kernel driver.

%prep
%setup -qc
mv *-flashcache-*/* .

%build
%if %{with kernel}
%build_kernel_modules -m flashcache
%build_kernel_modules -m flashcache-wt -C flashcache-wt
%endif

%if %{with userspace}
# as makefile aslo tries to build kernel part, we build userspace ourselves
cd src
%{__cc} %{rpmldflags} %{rpmcflags} -I./ -o utils/flashcache_create utils/flashcache_create.c
%{__cc} %{rpmldflags} %{rpmcflags} -I./ -o utils/flashcache_destroy utils/flashcache_destroy.c
%{__cc} %{rpmldflags} %{rpmcflags} -I./ -o utils/flashcache_load utils/flashcache_load.c
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT
%if %{with kernel}
%install_kernel_modules -m flashcache,flashcache-wt -d kernel/block
%endif

%if %{with userspace}
# as makefile aslo tries to build kernel part, we build userspace ourselves
install -d $RPM_BUILD_ROOT%{_sbindir}
install -p src/utils/flashcache_create $RPM_BUILD_ROOT%{_sbindir}
install -p src/utils/flashcache_destroy $RPM_BUILD_ROOT%{_sbindir}
install -p src/utils/flashcache_load $RPM_BUILD_ROOT%{_sbindir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-n kernel%{_alt_kernel}-block-flashcache
%depmod %{_kernel_ver}

%postun	-n kernel%{_alt_kernel}-block-flashcache
%depmod %{_kernel_ver}

%files
%defattr(644,root,root,755)
%doc README doc/*
%attr(755,root,root) %{_sbindir}/flashcache_create
%attr(755,root,root) %{_sbindir}/flashcache_destroy
%attr(755,root,root) %{_sbindir}/flashcache_load

%if %{with kernel}
%files -n kernel%{_alt_kernel}-block-flashcache
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/block/*.ko*
%endif
