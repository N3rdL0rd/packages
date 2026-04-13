%global _default_patch_fuzz 2
%global debug_package       %{nil}

Name:           vesktop
Version:        1.6.5
Release:        1%{?dist}
Summary:        Vesktop is a custom Discord desktop app

License:        GPL-3.0-only
URL:            https://github.com/Vencord/Vesktop

Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz
Source1:        vesktop.sh
Source2:        vesktop.desktop

BuildRequires:  nodejs-npm
BuildRequires:  pnpm

%description
Vesktop is a custom Discord desktop app aiming to give
you better performance and improve Linux support.

%prep
%autosetup -n Vesktop-%{version} -p1

%build
export COREPACK_ENABLE_STRICT=0
pnpm i
pnpm package:dir

%install
# 1. Create directories
mkdir -p %{buildroot}/opt/Vesktop
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps

cp -pr dist/linux-unpacked/* %{buildroot}/opt/Vesktop/
ln -s /opt/Vesktop/vesktop %{buildroot}%{_bindir}/vesktop
install -Dpm644 build/icon.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/vesktop.svg

cat <<EOF > %{buildroot}%{_datadir}/applications/vesktop.desktop
[Desktop Entry]
Name=Vesktop
GenericName=Internet Messenger
Comment=Vesktop Discord Client
Exec=vesktop %U
Icon=vesktop
Type=Application
Terminal=false
Categories=Network;InstantMessaging;Chat;
MimeType=x-scheme-handler/discord;
StartupWMClass=vesktop
EOF

%files
%license LICENSE
%doc README.md
/opt/Vesktop/
%{_bindir}/vesktop
%{_datadir}/applications/vesktop.desktop
%{_datadir}/icons/hicolor/scalable/apps/vesktop.svg

%changelog
%autochangelog