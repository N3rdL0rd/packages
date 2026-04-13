%global app_name paktool
%global repo_name alivecells
%global tag_name  paktool-v%{version}
%global debug_package %{nil}
%global __strip /bin/true

Name:           %{app_name}
Version:        0.0.4
Release:        1%{?dist}
Summary:        A command-line tool for expanding and creating Heaps.IO PAK archives.

License:        MIT
URL:            https://github.com/N3rdL0rd/%{repo_name}
Source0:        %{url}/archive/%{tag_name}.tar.gz

BuildRequires:  dotnet-sdk-10.0
Requires:       krb5-libs
Requires:       libicu
Requires:       openssl-libs
Requires:       zlib
Requires:       glibc

ExclusiveArch:  x86_64 aarch64

%description
A command-line tool for expanding and creating Heaps.IO PAK resource archives, based on Dead Cells' ModTools.

%prep
%autosetup -n %{repo_name}-%{tag_name}

%build
%ifarch x86_64
  %global dotnet_rid linux-x64
%endif
%ifarch aarch64
  %global dotnet_rid linux-arm64
%endif

# Move into the monorepo subdirectory
cd PAKTool

dotnet publish -c Release \
    -r %{dotnet_rid} \
    --self-contained true \
    -p:PublishSingleFile=true \
    -p:DebugSymbols=false \
    -p:DebugType=none \
    -o out

%install
install -d -m 755 %{buildroot}%{_bindir}

install -m 755 PAKTool/out/PAKTool %{buildroot}%{_bindir}/%{app_name}

%files
%license LICENSE
%{_bindir}/%{app_name}

%changelog
* Thu Jul 31 2025 N3rdL0rd <n3rdl0rd@proton.me> - 0.0.4-1
- Initial source-based build for COPR with monorepo support.