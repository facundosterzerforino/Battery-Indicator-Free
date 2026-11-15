#!/usr/bin/env python
"""Offline build of BatteryBot 10.0.1-beta1 (GPL-3.0) for Android 2.3 phones.

Explicit local inputs only: JDK, Android build-tools (aapt, zipalign, d8/R8,
apksigner), the API 24 android.jar (compile-time only) and the support-v4
24.1.1 AAR from Google's Maven (Apache 2.0). Signing key and password file
must be outside this repository.
"""
import argparse, hashlib, os, pathlib, shutil, subprocess, zipfile

SUPPORT_V4_SHA1 = '57c006a017aa2cbe3d32511e5ac28ee76cf9f51b'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for a in ('--jdk', '--build-tools', '--android-jar', '--support-aar', '--keystore', '--storepass-file'):
        p.add_argument(a, required=True)
    p.add_argument('--alias', default='music')
    a = p.parse_args()
    root = pathlib.Path(__file__).resolve().parent
    for secret in (a.keystore, a.storepass_file):
        if pathlib.Path(secret).resolve().is_relative_to(root):
            raise SystemExit('Signing files must be outside the source tree')
    aar = pathlib.Path(a.support_aar)
    if hashlib.sha1(aar.read_bytes()).hexdigest() != SUPPORT_V4_SHA1:
        raise SystemExit('support-v4 AAR checksum mismatch')
    sfx = '.exe' if os.name == 'nt' else ''
    jdk, bt = pathlib.Path(a.jdk), pathlib.Path(a.build_tools)
    java, javac = jdk / 'bin' / ('java' + sfx), jdk / 'bin' / ('javac' + sfx)
    aapt, align = bt / ('aapt' + sfx), bt / ('zipalign' + sfx)
    r8, signer = bt / 'lib' / 'd8.jar', bt / 'lib' / 'apksigner.jar'
    out = root / 'build'
    if out.exists(): shutil.rmtree(out)
    for d in ('gen', 'classes', 'dex', 'aar'): (out / d).mkdir(parents=True)
    run = lambda *c: subprocess.run([str(x) for x in c], cwd=root, check=True)
    with zipfile.ZipFile(aar) as z:
        z.extract('classes.jar', out / 'aar'); z.extract('libs/internal_impl-24.1.1.jar', out / 'aar'); z.extract('proguard.txt', out / 'aar')
    libs = [out / 'aar/classes.jar', out / 'aar/libs/internal_impl-24.1.1.jar']
    common = ('-M', root / 'AndroidManifest.xml', '-S', root / 'res', '-I', a.android_jar,
              '--min-sdk-version', '9', '--target-sdk-version', '24')
    run(aapt, 'package', '-f', '-m', '-J', out / 'gen', '-G', out / 'aapt-rules.pro', *common)
    srcs = [*sorted((root / 'src').rglob('*.java')), *sorted((out / 'gen').rglob('*.java'))]
    run(javac, '-encoding', 'UTF-8', '-source', '7', '-target', '7', '-g:none', '-nowarn', '-Xlint:-options',
        '-bootclasspath', a.android_jar, '-classpath', os.pathsep.join(map(str, libs)), '-d', out / 'classes', *srcs)
    classes = sorted((out / 'classes').rglob('*.class'))
    run(java, '-cp', r8, 'com.android.tools.r8.R8', '--release', '--min-api', '9', '--lib', a.android_jar,
        '--pg-conf', root / 'proguard-no-obfuscation', '--pg-conf', out / 'aapt-rules.pro', '--pg-conf', out / 'aar/proguard.txt',
        '--pg-map-output', out / 'mapping.txt', '--output', out / 'dex', *classes, *libs)
    unsigned, aligned, apk = out / 'unsigned.apk', out / 'aligned.apk', out / 'BatteryBot.apk'
    run(aapt, 'package', '-f', '-c', 'es,en,mdpi', *common, '-F', unsigned)
    with zipfile.ZipFile(unsigned, 'a', zipfile.ZIP_DEFLATED) as z:
        z.write(out / 'dex/classes.dex', 'classes.dex')
    run(align, '-f', '4', unsigned, aligned)
    run(java, '-jar', signer, 'sign', '--ks', a.keystore, '--ks-key-alias', a.alias, '--ks-pass', 'file:' + a.storepass_file,
        '--min-sdk-version', '9', '--v1-signing-enabled', 'true', '--v2-signing-enabled', 'false', '--v3-signing-enabled', 'false',
        '--out', apk, aligned)
    run(java, '-jar', signer, 'verify', '--min-sdk-version', '9', apk)
    print('APK:', apk, apk.stat().st_size, 'bytes, SHA256', hashlib.sha256(apk.read_bytes()).hexdigest())

if __name__ == '__main__':
    main()
