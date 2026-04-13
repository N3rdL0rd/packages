%global debug_package %{nil}

Name:           hlbc
Version:        0.8.0
Release:        1%{?dist}
Summary:        Command line interface for the HashLink bytecode disassembler

License:        MIT
URL:            https://github.com/N3rdL0rd/hlbc
Source0:        %{url}/archive/refs/heads/master.tar.gz

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  gcc

%description
A command line tool to disassemble and analyze HashLink bytecode (.hl files).

%prep
%autosetup -n hlbc-master

# remove gui to prevent errors
sed -i '/"crates\/hlbc-gui"/d' Cargo.toml

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