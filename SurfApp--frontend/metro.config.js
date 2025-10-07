const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Add 'css' to the asset extensions
config.resolver.assetExts.push('css');

// Add custom resolver to handle Mapbox issue
config.resolver.sourceExts = [...config.resolver.sourceExts, 'mjs'];

module.exports = config;