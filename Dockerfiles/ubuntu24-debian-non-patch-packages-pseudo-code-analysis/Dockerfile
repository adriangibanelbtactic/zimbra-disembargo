# syntax=docker/dockerfile:1
FROM ubuntu:24.04

ARG ZIMBRA_DISEMBARGOER_UID=1000
ARG ZIMBRA_DISEMBARGOER_GID=1000

# The installer identifies this signing-key fingerprint. Fetching it separately
# keeps the verified NE archive out of the Docker build context.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        ca-certificates \
        curl \
        gpg \
    && curl --fail --location --silent --show-error \
        'https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x9BE6ED79' \
        | gpg --dearmor --output /etc/apt/trusted.gpg.d/zimbra.gpg \
    && gpg --show-keys --with-colons /etc/apt/trusted.gpg.d/zimbra.gpg \
        | awk -F: '$1 == "fpr" { print $10; exit }' \
        | grep --fixed-strings --line-regexp '254F9170B966D193D6BAD300D5CEF8BF9BE6ED79'

COPY Dockerfiles/repositories/debian-repos/ /etc/apt/sources.list.d/

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --yes --no-install-recommends \
        apt-utils \
        bash \
        diffutils \
        file \
        findutils \
        gawk \
        git \
        jq \
        less \
        lz4 \
        python3 \
        sudo \
        unzip \
        xz-utils \
        zip \
    && rm --force --recursive /var/lib/apt/lists/* \
    && (getent group "${ZIMBRA_DISEMBARGOER_GID}" >/dev/null || groupadd --gid "${ZIMBRA_DISEMBARGOER_GID}" disembargo) \
    && existing_user="$(getent passwd "${ZIMBRA_DISEMBARGOER_UID}" | cut --delimiter=: --fields=1)" \
    && if [ "${existing_user}" = disembargo ]; then :; \
       elif [ -n "${existing_user}" ]; then usermod --login disembargo --home /home/disembargo --move-home "${existing_user}"; \
       else useradd --create-home --gid "${ZIMBRA_DISEMBARGOER_GID}" --shell /bin/bash --uid "${ZIMBRA_DISEMBARGOER_UID}" disembargo; fi \
    && printf '%s\n' 'disembargo ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/disembargo \
    && chmod 0440 /etc/sudoers.d/disembargo \
    && mkdir /work /results \
    && chown "disembargo:${ZIMBRA_DISEMBARGOER_GID}" /work /results

ENV HOME=/home/disembargo \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

USER disembargo
WORKDIR /work
CMD ["sleep", "infinity"]
