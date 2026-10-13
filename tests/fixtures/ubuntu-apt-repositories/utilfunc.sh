configurePackageServer() {
  TMP_PACKAGE_SERVER="repo.example.test"
  if [ $PLATFORM = "UBUNTU24_64" ]; then
    repo="noble"
  elif [ $PLATFORM = "UBUNTU22_64" ]; then
    repo="jammy"
  fi
  if [ "$PLATFORM" = "UBUNTU24_64" ]; then
    cat > /etc/apt/sources.list.d/zimbra.sources << EOF
Types: deb deb-src
URIs: https://$PACKAGE_SERVER/apt/1010
Suites: $repo
Components: zimbra
Architectures: amd64
Signed-By: /etc/apt/keyrings/zimbra.gpg
EOF
    if [ "x$ZMTYPE_INSTALLABLE" = "xNETWORK" ]; then
      cat >> /etc/apt/sources.list.d/zimbra.sources << EOF

Types: deb
URIs: https://$PACKAGE_SERVER/apt/1010-ne
Suites: $repo
Components: zimbra
Architectures: amd64
Signed-By: /etc/apt/keyrings/zimbra.gpg
EOF
      cat > /etc/apt/sources.list.d/zimbra-onlyoffice.sources << EOF
Types: deb
URIs: https://$PACKAGE_SERVER/apt/onlyoffice-1010
Suites: $repo
Components: zimbra
Architectures: amd64
Signed-By: /etc/apt/keyrings/zimbra.gpg
EOF
    fi
  fi
}
