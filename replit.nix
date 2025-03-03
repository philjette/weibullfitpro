{pkgs}: {
  deps = [
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
    pkgs.glibcLocales
    pkgs.xsimd
    pkgs.pkg-config
    pkgs.libxcrypt
  ];
}
