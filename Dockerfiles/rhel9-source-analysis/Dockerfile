# syntax=docker/dockerfile:1
FROM rockylinux:9

ARG ZIMBRA_DISEMBARGOER_UID=1000
ARG ZIMBRA_DISEMBARGOER_GID=1000

RUN dnf --assumeyes install \
        bash \
        ca-certificates \
        diffutils \
        file \
        findutils \
        gawk \
        git \
        gzip \
        jq \
        less \
        make \
        patch \
        python3 \
        rpm \
        rpm-build \
        sudo \
        tar \
        unzip \
        which \
        xz \
        zip \
    && dnf clean all \
    && rm -rf /var/cache/dnf \
    && groupadd --gid "${ZIMBRA_DISEMBARGOER_GID}" disembargo \
    && useradd --create-home --gid disembargo --shell /bin/bash \
        --uid "${ZIMBRA_DISEMBARGOER_UID}" disembargo \
    && printf '%s\n' 'disembargo ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/disembargo \
    && chmod 0440 /etc/sudoers.d/disembargo \
    && mkdir /work /results \
    && chown disembargo:disembargo /work /results

ENV HOME=/home/disembargo \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

USER disembargo
WORKDIR /work

# The launcher replaces this with the same command after creating the named
# container. Keeping it alive makes iterative docker exec sessions possible.
CMD ["sleep", "infinity"]
