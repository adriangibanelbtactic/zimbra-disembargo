configurePackageServer() {
  TMP_PACKAGE_SERVER="repo.example.test"
  if [ $PLATFORM = "RHEL8_64" ]; then
    repo="rhel8"
  elif [ $PLATFORM = "RHEL9_64" ]; then
    repo="rhel9"
  fi
cat > /etc/yum.repos.d/zimbra.repo <<EOF
[zimbra-oss]
name=Example OSS
baseurl=https://$PACKAGE_SERVER/rpm/1010/$repo
EOF
if [ x"$ZMTYPE_INSTALLABLE" = "xNETWORK" ]; then
cat >> /etc/yum.repos.d/zimbra.repo <<EOF
[zimbra-network]
name=Example Network
baseurl=https://$PACKAGE_SERVER/rpm/1010-ne/$repo
EOF
cat > /etc/yum.repos.d/zimbra-onlyoffice.repo <<EOF
[zimbra-onlyoffice]
name=Example OnlyOffice
baseurl=https://$PACKAGE_SERVER/rpm/onlyoffice-1010/$repo
EOF
fi
}
