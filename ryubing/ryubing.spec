%global debug_package %{nil}
%global __strip /bin/true

# ---------------------------------------------------------------
# ToT tracking: bump these two globals to update to a new build.
# For canary: grab the tag from https://git.ryujinx.app/ryubing/ryujinx/releases
# For stable: use the semver tag (e.g. 1.3.3)
# ---------------------------------------------------------------
%global upstream_version 1.3.279
%global channel          canary

# Shorthand used in the Release: field so stable vs canary builds
# don't collide in the same repo.
%global relchannel %{channel}

Name:           ryubing
# Canary versions are higher than stable; use the upstream tag verbatim.
Version:        %{upstream_version}
Release:        1.%{relchannel}%{?dist}
Summary:        A Nintendo Switch emulator (Ryujinx community fork)

License:        MIT
URL:            https://git.ryujinx.app/ryubing/ryujinx
# Forgejo/Gitea archive URL: extracts to ryujinx/
Source0:        %{url}/archive/%{upstream_version}.tar.gz#/ryubing-%{upstream_version}.tar.gz
Patch0:         hidpi-wayland.patch

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
and improvements after the original Ryujinx project ceased active
maintenance. This package tracks the %{channel} channel.

%prep
# Forgejo archives extract to just the repo name without a version suffix.
%autosetup -p1 -n ryujinx

# Provide NuGet sources: nuget.org for everything except the Ryubing-hosted
# LibHac alpha, which lives on the project's own package registry.
cat > nuget.config << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <packageSources>
        <clear />
        <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
        <add key="RyubingRegistry" value="https://git.ryujinx.app/api/packages/projects/nuget/index.json" />
    </packageSources>
    <packageSourceMapping>
        <packageSource key="nuget.org">
            <package pattern="*" />
        </packageSource>
        <packageSource key="RyubingRegistry">
            <package pattern="Ryujinx.LibHac" />
        </packageSource>
    </packageSourceMapping>
</configuration>
EOF

# Stamp version/channel strings into the build metadata.
sed -r -i 's/%%RYUJINX_BUILD_VERSION%%/%{upstream_version}/g' \
    src/Ryujinx.Common/ReleaseInformation.cs
sed -r -i 's/%%RYUJINX_BUILD_GIT_HASH%%/%{upstream_version}-%{release}/g' \
    src/Ryujinx.Common/ReleaseInformation.cs
sed -r -i 's/%%RYUJINX_TARGET_RELEASE_CHANNEL_NAME%%/%{channel}/g' \
    src/Ryujinx.Common/ReleaseInformation.cs
sed -r -i 's/%%RYUJINX_CONFIG_FILE_NAME%%/Config\.json/g' \
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
    -p:Version=%{upstream_version} \
    -p:DebugType=embedded \
    -p:ExtraDefineConstants=DISABLE_UPDATER \
    -o publish \
    src/Ryujinx

%install
install -d -m 755 %{buildroot}/opt/ryubing
cp -pr publish/* %{buildroot}/opt/ryubing/
# Remove macOS-only JIT support dylib that has no business in an RPM.
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
* Wed Apr 29 2026 N3rdL0rd <n3rdl0rd@proton.me> - 1.3.274-1.canary
- Update to canary 1.3.274 (ToT as of 2026-04-24).
- Switch Source0 to Forgejo archive URL for easy ToT tracking.
- Add channel macro; Release field now encodes stable vs canary.

* Tue Apr 28 2026 N3rdL0rd <n3rdl0rd@proton.me> - 1.3.3-1
- Initial package.