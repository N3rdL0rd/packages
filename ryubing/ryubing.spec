%global debug_package %{nil}
%global __strip /bin/true

Name:           ryubing
Version:        1.3.3
Release:        1%{?dist}
Summary:        A Nintendo Switch emulator (Ryujinx community fork)

License:        MIT
URL:            https://git.ryujinx.app/projects/Ryubing
Source0:        %{url}/archive/%{version}.tar.gz

BuildRequires:  dotnet-sdk-10.0
BuildRequires:  desktop-file-utils

Requires:       hicolor-icon-theme
Requires:       vulkan-loader
Requires:       mesa-vulkan-drivers
Suggests:       gamemode
Suggests:       ffmpeg-free

ExclusiveArch:  x86_64 aarch64

%description
Ryubing is a community-maintained fork of Ryujinx, a Nintendo Switch
emulator built with .NET and Avalonia. It provides continued development
and improvements after the original Ryujinx project ceased.

%prep
%autosetup -n ryubing

cat > global.json << 'EOF'
{
  "sdk": {
    "version": "10.0.100",
    "rollForward": "latestFeature"
  }
}
EOF

cat > nuget.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <packageSources>
        <clear />
        <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
        <add key="LibHacAlpha" value="https://git.ryujinx.app/api/packages/projects/nuget/index.json" />
    </packageSources>
    <packageSourceMapping>
        <packageSource key="nuget.org">
            <package pattern="*" />
        </packageSource>
        <packageSource key="LibHacAlpha">
            <package pattern="Ryujinx.LibHac" />
        </packageSource>
    </packageSourceMapping>
</configuration>
EOF

sed -r -i 's/\%\%RYUJINX_BUILD_VERSION\%\%/%{version}/g' \
    src/Ryujinx.Common/ReleaseInformation.cs
sed -r -i 's/\%\%RYUJINX_BUILD_GIT_HASH\%\%/%{version}-%{release}/g' \
    src/Ryujinx.Common/ReleaseInformation.cs
sed -r -i 's/\%\%RYUJINX_TARGET_RELEASE_CHANNEL_NAME\%\%/release/g' \
    src/Ryujinx.Common/ReleaseInformation.cs
sed -r -i 's/\%\%RYUJINX_CONFIG_FILE_NAME\%\%/Config\.json/g' \
    src/Ryujinx.Common/ReleaseInformation.cs

%build
%ifarch x86_64
%global dotnet_rid linux-x64
%endif
%ifarch aarch64
%global dotnet_rid linux-arm64
%endif

export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=1
export NUGET_XMLDOC_MODE=skip

dotnet publish -c Release \
    -r %{dotnet_rid} \
    --self-contained \
    -p:Version=%{version} \
    -p:DebugType=embedded \
    -p:ExtraDefineConstants=DISABLE_UPDATER \
    -o publish \
    src/Ryujinx

%install
install -d -m 755 %{buildroot}/opt/ryubing
cp -pr publish/* %{buildroot}/opt/ryubing/
rm -f %{buildroot}/opt/ryubing/libarmeilleure-jitsupport.dylib
chmod 0755 %{buildroot}/opt/ryubing/Ryujinx %{buildroot}/opt/ryubing/Ryujinx.sh

install -d -m 755 %{buildroot}%{_bindir}
cat <<'EOF' > %{buildroot}%{_bindir}/ryubing
#!/bin/sh
exec env LANG=C.UTF-8 DOTNET_EnableAlternateStackCheck=1 /opt/ryubing/Ryujinx "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/ryubing

install -d -m 755 %{buildroot}%{_datadir}/applications
cat <<'EOF' > %{buildroot}%{_datadir}/applications/ryubing.desktop
[Desktop Entry]
Version=1.0
Name=Ryubing
Type=Application
Icon=ryubing
Exec=ryubing %f
Comment=A Nintendo Switch Emulator
GenericName=Nintendo Switch Emulator
Terminal=false
Categories=Game;Emulator;
MimeType=application/x-nx-nca;application/x-nx-nro;application/x-nx-nso;application/x-nx-nsp;application/x-nx-xci;
Keywords=Switch;Nintendo;Emulator;
StartupWMClass=Ryujinx
PrefersNonDefaultGPU=true
EOF

install -d -m 755 %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -p -m 644 distribution/misc/Logo.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/ryubing.svg

install -d -m 755 %{buildroot}%{_datadir}/mime/packages
install -p -m 644 distribution/linux/mime/Ryujinx.xml \
    %{buildroot}%{_datadir}/mime/packages/ryubing.xml

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/ryubing.desktop

%post
update-desktop-database &>/dev/null || :
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
update-mime-database %{_datadir}/mime &>/dev/null || :

%postun
update-desktop-database &>/dev/null || :
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
update-mime-database %{_datadir}/mime &>/dev/null || :

%files
%license LICENSE.txt
%doc README.md
/opt/ryubing/
%{_bindir}/ryubing
%{_datadir}/applications/ryubing.desktop
%{_datadir}/icons/hicolor/scalable/apps/ryubing.svg
%{_datadir}/mime/packages/ryubing.xml

%changelog
* Tue Apr 28 2026 N3rdL0rd <n3rdl0rd@proton.me> - 1.3.3-1
- Initial package.
