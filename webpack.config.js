const webpack = require('webpack');
const path = require('path');

const UglifyJSPlugin = require('uglifyjs-webpack-plugin');

module.exports = {
    module: {
        rules: [
            {
                test: /\.tsx?$/,
                use: 'ts-loader',
                exclude: /node_modules/
            },
            {
                include: [path.resolve(__dirname, 'src')],
                loader: 'babel-loader',

                options: {
                    plugins: ['syntax-dynamic-import'],

                    presets: [
                        [
                            '@babel/preset-env',
                            {
                                modules: false
                            }
                        ]
                    ]
                },

                test: /\.js$/
            },
            {
                test: /\.(scss|css)$/,

                use: [
                    {
                        loader: 'style-loader'
                    },
                    {
                        loader: 'css-loader'
                    },
                    {
                        loader: 'sass-loader'
                    }
                ]
            }
        ]
    },

    entry: {
        student_view: './onshape_xblock/static/js/src/student_view.ts',
        studio_view: './onshape_xblock/static/js/src/studio_view.ts',
        oauth_login_view: './onshape_xblock/static/js/src/oauth_login_view.ts'
    },

    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'onshape_xblock/static/js/dist')
    },

    resolve: {
        extensions: ['.tsx', '.ts', '.js', '.d.ts']
    },

    mode: 'development',

    optimization: {
        splitChunks: {
            cacheGroups: {
                vendors: {
                    priority: -10,
                    test: /[\\/]node_modules[\\/]/
                }
            },

            chunks: 'async',
            minChunks: 1,
            minSize: 30000,
            name: true
        }
    },

    devtool: 'inline-source-map',
    watch: true

    // plugins: [
    //     new webpack.SourceMapDevToolPlugin({
    //           append: '\n//# sourceMappingURL=http://localhost:9000/[url]',
    //             filename: '[name].map'
    //     })
    //   ],
    // devServer: {
    //     contentBase: './onshape_xblock/static/js/dist',
    //     compress: true,
    //     port: 9000
    //   }
};


