%global debug_package %{nil}

Name:           hlbc
Version:        0.8.0
Release:        1%{?dist}
Summary:        HashLink bytecode disassembler and decompiler

License:        MIT
URL:            https://github.com/Gui-Yom/hlbc
Source0:        %{url}/archive/refs/heads/master.tar.gz

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc

%description
A command line tool to disassemble and decompile HashLink bytecode (.hl files).

%prep
%autosetup -n hlbc-master

%build
cargo build --release -p hlbc-cli

%install
mkdir -p %{buildroot}%{_bindir}

install -Dpm 0755 target/release/hlbc %{buildroot}%{_bindir}/hlbc

%files
%license LICENSE
%{_bindir}/hlbc

%changelog
%autochangelog