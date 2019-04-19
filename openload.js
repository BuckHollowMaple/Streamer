const openload = (id, cb) => {
  request('https://openload.co/embed/' + id, text => {
    let r = text.indexOf('streamurl') - 18
    let l = text.lastIndexOf('>', r) + 1
    var _0x1ca2d1 = {
      '\x76\x70\x42': function _0x5db332(_0x4bcf06, _0x3bac1a) {
        return _0x4bcf06 < _0x3bac1a;
      },
      '\x4f\x61\x68': function _0x45ecc9(_0x47b854, _0x37aa20) {
        return _0x47b854 + _0x37aa20;
      },
      '\x49\x62\x4c': function _0x331a2f(_0x1db2d8, _0xdd767a, _0x2cbead) {
        return _0x1db2d8(_0xdd767a, _0x2cbead);
      },
      '\x77\x64\x68': function _0x3d60a9(_0x2127eb, _0x8756bc) {
        return _0x2127eb == _0x8756bc;
      },
      '\x49\x53\x63': function _0x281f64(_0xed1a8d, _0x3b66ad) {
        return _0xed1a8d % _0x3b66ad;
      },
      '\x70\x65\x70': function _0xd12b43(_0x1d0842, _0x1cd9ce, _0x2ffa29) {
        return _0x1d0842(_0x1cd9ce, _0x2ffa29);
      },
      '\x6b\x56\x74': function _0x36e0cc(_0x5d218e, _0x322d54) {
        return _0x5d218e != _0x322d54;
      },
      '\x75\x4c\x4b': function _0x58d581(_0x338b48, _0x50fadb) {
        return _0x338b48 < _0x50fadb;
      },
      '\x6b\x6c\x4d': function _0x23c488(_0x2974b5, _0x6c1f22) {
        return _0x2974b5 - _0x6c1f22;
      },
      '\x48\x7a\x74': function _0x16209e(_0x2db611, _0x34221c) {
        return _0x2db611(_0x34221c);
      },
      '\x56\x4a\x63': function _0x51784d(_0x163a81, _0x171e4a) {
        return _0x163a81 - _0x171e4a;
      },
      '\x4a\x4e\x74': function _0x13839a(_0x52bacf, _0xdb40cd) {
        return _0x52bacf - _0xdb40cd;
      },
      '\x56\x46\x70': function _0x3ecc8a(_0x2e0c2e, _0x1456c4) {
        return _0x2e0c2e + _0x1456c4;
      },
      '\x47\x58\x41': function _0x2ed252(_0x27fc6d, _0x42a347) {
        return _0x27fc6d - _0x42a347;
      },
      '\x79\x71\x4f': function _0x24d82b(_0xcd0acf, _0x3272e9) {
        return _0xcd0acf + _0x3272e9;
      },
      '\x4a\x72\x4a': function _0x11e4b5(_0x159b14, _0x444b17) {
        return _0x159b14 < _0x444b17;
      },
      '\x54\x41\x6b': function _0x2bdc14(_0x123b5e, _0x486155) {
        return _0x123b5e + _0x486155;
      },
      '\x72\x75\x56': function _0xbfd31a(_0x28aaee, _0x1f0148) {
        return _0x28aaee / _0x1f0148;
      }
    };
    var _0x38cd7f = '\x37\x7c\x35\x7c\x38\x7c\x36\x7c\x32\x7c\x31\x7c\x34\x7c\x30\x7c\x33' ['\x73\x70\x6c\x69\x74']('\x7c'),
    _0x15954b = 0x0;
    while (!![]) {
      switch (_0x38cd7f[_0x15954b++]) {
        case '\x30':
          for (var _0x53ad1a = 0x0; _0x1ca2d1['\x76\x70\x42'](_0x74f1a2, _0x59fb49['\x6c\x65\x6e\x67\x74\x68']);) {
            var _0x4bf55a = _0x59fb49['\x73\x75\x62\x73\x74\x72\x69\x6e\x67'](_0x74f1a2, _0x1ca2d1['\x4f\x61\x68'](_0x74f1a2, 0x2)),
            _0x57acc0 = _0x59fb49['\x73\x75\x62\x73\x74\x72\x69\x6e\x67'](_0x74f1a2, _0x1ca2d1['\x4f\x61\x68'](_0x74f1a2, 0x3)),
            _0x2f417a = _0x1ca2d1['\x49\x62\x4c'](parseInt, _0x4bf55a, 0x10);
            _0x74f1a2 += 0x2, _0x1ca2d1['\x77\x64\x68'](_0x1ca2d1['\x49\x53\x63'](_0x53ad1a, 0x3), 0x0) ? (_0x2f417a = _0x1ca2d1['\x70\x65\x70'](parseInt, _0x57acc0, 0x8), _0x74f1a2 += 0x1) : _0x1ca2d1['\x77\x64\x68'](_0x1ca2d1['\x49\x53\x63'](_0x53ad1a, 0x2), 0x0) && _0x1ca2d1['\x6b\x56\x74'](0x0, _0x53ad1a) && _0x1ca2d1['\x75\x4c\x4b'](_0x59fb49[_0x1ca2d1['\x6b\x6c\x4d'](_0x53ad1a, 0x1)]['\x63\x68\x61\x72\x43\x6f\x64\x65\x41\x74'](0x0), 0x3c) && (_0x2f417a = _0x1ca2d1['\x70\x65\x70'](parseInt, _0x57acc0, 0xa), _0x74f1a2 += 0x1);
            var _0x1e6524 = _0x4d1693[_0x1ca2d1['\x49\x53\x63'](_0x53ad1a, 0x8)];
            _0x2f417a ^= 0xd5, _0x2f417a ^= _0x1e6524, _0x466793['\x70\x75\x73\x68'](String['\x66\x72\x6f\x6d\x43\x68\x61\x72\x43\x6f\x64\x65'](_0x2f417a)), _0x53ad1a += 0x1;
          }
          continue;
        case '\x31':
          var _0x59fb49 = _0x498b9f['\x6a\x6f\x69\x6e'](''),
          _0x466793 = [];
          continue;
        case '\x32':
          _0x498b9f['\x73\x70\x6c\x69\x63\x65'](_0x231a0b, 0x18);
          continue;
        case '\x33':
          cb('https://openload.co/stream/' + _0x466793['\x6a\x6f\x69\x6e']('') + '?mime=true');
          continue;
        case '\x34':
          _0x74f1a2 = 0x0;
          continue;
        case '\x35':
          _0x231a0b = Math['\x6d\x69\x6e'](_0x4adcec, _0x1ca2d1['\x56\x4a\x63'](_0x1ca2d1['\x4a\x4e\x74'](_0xb9a0d8['\x6c\x65\x6e\x67\x74\x68'], 0x18), 0x2));
          continue;
        case '\x36':
          var _0x498b9f = _0xb9a0d8['\x73\x70\x6c\x69\x74']('');
          continue;
        case '\x37':
          var _0xb9a0d8 = text.substring(l, r),
          _0x23ead9 = _0xb9a0d8['\x63\x68\x61\x72\x43\x6f\x64\x65\x41\x74'](0x0),
          _0x231a0b = _0x1ca2d1['\x47\x58\x41'](_0x23ead9, 0x37),
          _0x4adcec = Math['\x6d\x61\x78'](0x2, _0x231a0b);
          continue;
        case '\x38':
          for (var _0xfb2ce1 = _0xb9a0d8['\x73\x75\x62\x73\x74\x72\x69\x6e\x67'](_0x231a0b, _0x1ca2d1['\x79\x71\x4f'](_0x231a0b, 0x18)), _0x4d1693 = new Array(0x8), _0x74f1a2 = 0x0; _0x1ca2d1['\x4a\x72\x4a'](_0x74f1a2, _0xfb2ce1['\x6c\x65\x6e\x67\x74\x68']);) {
            var _0x528aeb = _0xfb2ce1['\x73\x75\x62\x73\x74\x72\x69\x6e\x67'](_0x74f1a2, _0x1ca2d1['\x54\x41\x6b'](_0x74f1a2, 0x3));
            _0x4d1693[_0x1ca2d1['\x72\x75\x56'](_0x74f1a2, 0x3)] = _0x1ca2d1['\x70\x65\x70'](parseInt, _0x528aeb, 0x8), _0x74f1a2 += 0x3;
          }
          continue;
      }
      break;
    }
  })
}
